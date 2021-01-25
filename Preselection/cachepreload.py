def dask_setup(worker):
    import os

    def get_classads():
        fname = os.getenv("_CONDOR_JOB_AD")
        if not fname:
            return {}
        d = {}
        with open(fname) as fh:
            for line in fh:
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip().lstrip('"').strip('"')
        return d
    worker.classads = get_classads()

    worker.array_cache = None
    worker.tree_cache = {}
    worker.nevents = 0
    try:
        import uproot
        worker.array_cache = uproot.ArrayCache("6 GB")
    except ImportError as e:
        print(e, "so we can't make a global ArrayCache")
    except AttributeError as e:
        print(e, " Maybe this is an older version of uproot without ArrayCache?")

    def cachesize_metric(worker):
        if hasattr(worker,"array_cache"):
            return "{:.2f}GB".format(worker.array_cache._cache.currsize/1e9)
        return 0
    def numtreescached_metric(worker):
        if hasattr(worker,"tree_cache"):
            return len(list(worker.tree_cache.keys()))
        return 0
    def nevents_metric(worker):
        if hasattr(worker,"nevents"):
            return "{:.2f}M".format(worker.nevents/1e6)
        return 0

    worker.metrics["cachesize"] = cachesize_metric
    worker.metrics["numtreescached"] = numtreescached_metric
    worker.metrics["eventsprocessed"] = nevents_metric

    try:
        # Load some imports initially
        import coffea.processor
        import coffea.executor
    except:
        pass
