import functools
import time
import uproot3
from dask.distributed import as_completed
from collections import defaultdict
from tqdm.auto import tqdm

def bokeh_output_notebook():
    from bokeh.io import output_notebook
    output_notebook()

def plot_timeflow(taskstream):
    """
    taskstream from `client.get_task_stream(count=len(futures))`
    """
    from bokeh.io import show, output_notebook
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    import pandas as pd

    df = pd.DataFrame(taskstream)
    df["tstart"] = df["startstops"].str[0].str[1]
    df["tstop"] = df["startstops"].str[0].str[2]
    df = df[["worker","tstart","tstop"]].sort_values(["worker","tstart"])
    df[["tstart","tstop"]] -= df["tstart"].min()
    df["worker"] = df["worker"].str.replace("tcp://","")

    if df["tstop"].max() > 10.: mult, unit = 1, "s"
    else: mult, unit = 1000, "ms"

    df[["tstart","tstop"]] *= mult
    df["duration"] = df["tstop"] - df["tstart"]

    group = df.groupby("worker")
    source = ColumnDataSource(group)

    wtime = (df["tstop"]-df["tstart"]).sum()
    nworkers = df["worker"].nunique()
    ttime = df["tstop"].max()*nworkers
    title = (", ".join([
        "{} workers".format(nworkers),
        "efficiency = {:.1f}%".format(100.0*wtime/ttime),
        "median task time = {:.2f}{}".format(group.apply(lambda x:x["tstop"]-x["tstart"]).median(),unit),
        "median intertask time = {:.2f}{}".format(group.apply(lambda x:x["tstart"].shift(-1)-x["tstop"]).median(),unit),
        ]))

    p = figure(y_range=group, x_range=[0,df["tstop"].max()], title=title,
               tooltips = [
                   ["worker","@worker"],
                   ["start","@{tstart}"+unit],
                   ["stop","@{tstop}"+unit],
                   ["duration","@{duration}"+unit],
               ],
              )
    p.hbar(y="worker", left="tstart", right="tstop", height=1.0, line_color="black", source=df)
    p.xaxis.axis_label = "elapsed time since start ({})".format(unit)
    p.yaxis.axis_label = "worker"
    p.plot_width = 800
    p.plot_height = 350

    try:
        show(p)
    except:
        show(p)

@functools.lru_cache(maxsize=256)
def get_chunking(filelist, chunksize, treename="Events", workers=12, skip_bad_files=False, xrootd=False, client=None, use_dask=False):
    """
    Return 2-tuple of
    - chunks: triplets of (filename,entrystart,entrystop) calculated with input `chunksize` and `filelist`
    - total_nevents: total event count over `filelist`
    """
    import uproot3
    from tqdm.auto import tqdm
    import concurrent.futures

    if xrootd:
        temp = []
        for fname in filelist:
            if fname.startswith("/hadoop/cms"):
                temp.append(fname.replace("/hadoop/cms","root://redirector.t2.ucsd.edu/"))
            else:
                temp.append(fname.replace("/store/","root://xrootd.t2.ucsd.edu:2040//store/"))
        filelist = temp

    chunksize = int(chunksize)
    chunks = []
    nevents = 0
    
    if use_dask:
        if not client:
            from dask.distributed import get_client
            client = get_client()
        def numentries(fname):
            import uproot3
            try:
                return (fname,uproot3.numentries(fname,treename))
            except:
                return (fname,-1)
        futures = client.map(numentries, filelist)
        info = []
        for future, result in tqdm(as_completed(futures, with_results=True), total=len(futures)):
            info.append(result)
        for fn, nentries in info:
            if nentries < 0:
                if skip_bad_files:
                    print("Skipping bad file: {}".format(fn))
                    continue
                else: raise RuntimeError("Bad file: {}".format(fn))
            nevents += nentries
            for index in range(nentries // chunksize + 1):
                chunks.append((fn, chunksize*index, min(chunksize*(index+1), nentries)))
    else:
        if skip_bad_files:
            # slightly slower (serial loop), but can skip bad files
            for fname in tqdm(filelist):
                try:
                    items = uproot3.numentries(fname, treename, total=False).items()
                except (IndexError, ValueError) as e:
                    print("Skipping bad file", fname)
                    continue
                for fn, nentries in items:
                    nevents += nentries
                    for index in range(nentries // chunksize + 1):
                        chunks.append((fn, chunksize*index, min(chunksize*(index+1), nentries)))
        else:
            executor = None if len(filelist) < 5 else concurrent.futures.ThreadPoolExecutor(min(workers, len(filelist)))
            for fn, nentries in uproot3.numentries(filelist, treename, total=False, executor=executor).items():
                nevents += nentries
                for index in range(nentries // chunksize + 1):
                    chunks.append((fn, chunksize*index, min(chunksize*(index+1), nentries)))

    return chunks, nevents


def combine_dicts(dicts):
    new_dict = dict()
    for d in dicts:
        for k,v in d.items():
            if k not in new_dict:
                new_dict[k] = v
            else:
                new_dict[k] += v
    return new_dict

def clear_tree_cache(client=None):
    if not client:
        from dask.distributed import get_client
        client = get_client()
    def f():
        from dask.distributed import get_worker
        worker = get_worker()
        if hasattr(worker, "tree_cache"):
            worker.tree_cache.clear()
    client.run(f)


def get_results(func, fnames, chunksize=250e3, client=None, use_tree_cache=False):
    if not client:
        from dask.distributed import get_client
        client = get_client()
    print("Making chunks for workers")
    chunks, nevents_total = get_chunking(tuple(fnames), chunksize=chunksize, use_dask=True)
    print(f"Processing {len(chunks)} chunks")
    process = use_chunk_input(func, use_tree_cache=use_tree_cache)
    
    chunk_workers = None
    if use_tree_cache:
        def f():
            from dask.distributed import get_worker
            worker = get_worker()
            return list(worker.tree_cache.keys())
        filename_to_worker = defaultdict(list)
        for worker, filenames in client.run(f).items():
            for filename in filenames:
                filename_to_worker[filename].append(worker)
        chunk_workers = [filename_to_worker[chunk[0]] for chunk in chunks]

    futures = client.map(process, chunks, workers=chunk_workers)
    t0 = time.time()
    bar = tqdm(total=nevents_total, unit="events", unit_scale=True)
    ac = as_completed(futures, with_results=True)
    results = []
    for future, result in ac:
        results.append(result)
        bar.update(result["nevents_processed"])
    bar.close()
    t1 = time.time()
    results = combine_dicts(results)
    nevents_processed = results["nevents_processed"]
    print(f"Processed {nevents_processed:.5g} input events in {t1-t0:.1f}s ({1.0e-3*nevents_processed/(t1-t0):.2f}kHz)")
    return results


class DataFrameWrapper(object):
    def __init__(self, filename, entrystart=None, entrystop=None, treename="Events", use_tree_cache=False):
        self.filename = filename
        self.entrystart = entrystart
        self.entrystop = entrystop
        self.treename = treename
        self.data = dict()
        
        from dask.distributed import get_worker
        worker = get_worker()
        if use_tree_cache and hasattr(worker, "tree_cache"):
            cache = worker.tree_cache
            if filename not in cache:
                cache[filename] = uproot3.open(filename)["Events"]
            self.t = cache[filename]
        else:
            self.t = uproot3.open(filename)["Events"]

    def __getitem__(self, key):
        if key not in self.data:
            self.data[key] = self.t.array(key, entrystart=self.entrystart, entrystop=self.entrystop)
        return self.data[key]

    def __len__(self):
        if None not in [self.entrystart, self.entrystop]:
            return self.entrystop-self.entrystart
        return len(self.t)

def use_chunk_input(func, **kwargs):
    def wrapper(chunk):
        df = DataFrameWrapper(*chunk, **kwargs)
        t0 = time.time()
        out = func(df)
        t1 = time.time()
        out["nevents_processed"] = len(df)
        out["t_start"] = [t0]
        out["t_stop"] = [t1]
        try:
            from dask.distributed import get_worker
            out["worker_name"] = [get_worker().address]
        except:
            out["worker_name"] = ["local"]
        return out
    return wrapper

def plot_timeflow(results):
    from bokeh.io import show, output_notebook
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    import pandas as pd

    output_notebook()

    df = pd.DataFrame()
    df["worker"] = results["worker_name"]
    df["tstart"] = results["t_start"]
    df["tstop"] = results["t_stop"]
    df[["tstart","tstop"]] -= df["tstart"].min()
    df["worker"] = df["worker"].astype("category").cat.codes

    mult, unit = 1, "s"

    df[["tstart","tstop"]] *= mult
    df["duration"] = df["tstop"] - df["tstart"]

    group = df.groupby("worker")
    source = ColumnDataSource(group)

    wtime = (df["tstop"]-df["tstart"]).sum()
    nworkers = df["worker"].nunique()
    ttime = df["tstop"].max()*nworkers
    title = (", ".join([
        "{} workers".format(nworkers),
        "efficiency = {:.1f}%".format(100.0*wtime/ttime),
        "median task time = {:.2f}{}".format(group.apply(lambda x:x["tstop"]-x["tstart"]).median(),unit),
        "median intertask time = {:.2f}{}".format(group.apply(lambda x:x["tstart"].shift(-1)-x["tstop"]).median(),unit),
        ]))

    p = figure(
        title=title,
               tooltips = [
                   ["worker","@worker"],
                   ["start","@{tstart}"+unit],
                   ["stop","@{tstop}"+unit],
                   ["duration","@{duration}"+unit],
               ],
              )
    p.hbar(y="worker", left="tstart", right="tstop", height=1.0, line_color="black", source=df)
    p.xaxis.axis_label = "elapsed time since start ({})".format(unit)
    p.yaxis.axis_label = "worker"
    p.plot_width = 600
    p.plot_height = 300

    show(p)

