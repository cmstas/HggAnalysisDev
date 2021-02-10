# Instructions for running looper tool `loop.py`
1a. If you want to run over a set of samples that are not already in one of the `data/samples...` files, create a `json` file with your desired samples, adding them with the following fields:  
`"sample_name" : { # sample name will be used to identify this sample later in MVA training/SR optimization  

      "resonant" : true/false, # the looper will treat resonant and non-resonant samples slightly differently, blinding non-resonant samples in the [120,130] GeV region  

      "fpo" : N, # number of input nanoAOD skims for each job that the looper submits  

      "process_id" : N, # this is will be stored as a column in the output dataframe to distinguish which process this is -- usually, make sure you pick a different process_id from all other samples (sometimes you might want to identify multiple samples with the same process_id, e.g. HT-binned samples of the same process)  

      "2016" : {  

          "paths" : ["/path1", "/path2"],  

          "metadata" : { "xs" : xs in pb }  

      }   

      "2017" : {  

      . . .  

      }  

 }`  

1b. Calculate `scale1fb` for your new samples with `scripts/scale1fb.py`  

2. Run `loop.py` -- arguments:  
    - `samples`: give the path to the json file containing your samples  
    - `selections`: string identifying which selection you want to perform (make sure it is implemented in `helpers/loop_helper.py:select_events`  
    - `years`: comma-separated list of years to run over (should be a subset of "2016,2017,2018")  
    - `options`: `json` file which contains details such as which branches to load from nanoAOD (load the minimal set for optimal speed), which branches to save in your output dataframe, and selection options (e.g. cut values for physics objects, id requirements, etc)  
    - `systematics`: include systematics variations in output (not currently implemented, TO-DO)  
    - `output_tag`: string to append to your output dataframe to identify this particular looping  
    - `output_dir`: directory to place outputs in, defaults to `output`  
    - `batch`: pick between running locally, Dask (TO-DO), condor (TO-DO)  
    - `nCores`: if running locally, how many cores to use. If using more than a few, make sure to run with `/bin/nice -n 19 loop.py . . .`  to prevent from hogging UAF resources  
    - `debug`: int specifying the print-out level of diagnostic info (0 = minimal, 1 = more, ...)  
    - `fast`: if chosen, only runs 1 job per process (useful for debugging)  
    - `select_samples`: comma-separated list of samples to run over. This overrides the full list of samples in your samples `json`. Useful for debugging, otherwise you can ignore this argument.  
    - `dry_run`: don't actually submit the jobs (for debugging)  

# Basic steps

1. Pre-process skim (http://www.t2.ucsd.edu/tastwiki/bin/view/CMS/HHGgTauTauPostproc), turn files with large number of events (>1e6) into smaller chunks, for better parallization, save outcome in metadata for easy accessing

2. Process events into different categories, return a big dict with the following structure:

* dict[key1][key2]
    - key1: category name, e.g. 0lep_2tau
    - key2: histgram name, e.g. mtautau

* Needed scripts:

    - event_selector.py: contains basic functions for object and event selection
        + Hopefully this step can be fully absorbed into skim, but could be useful to have this functionalities just in case
    - looper_utils.py: some utils like deltaR cleanning
        + Put all useful functions that involve per-event loop here

* For now, I find it easier to dump histogram to disk (in the format of json) for later post-processing

    - In folder with name: hist

3. Assemble plots and make yield tables (read hist json from hist dir)

* This is where one manipulate plots and numbers

    - data/MC plots, shape comparison between two components...


# Dask related

- To use this set of code/notebook, follow the setup instruction from here: https://github.com/aminnj/daskucsd
    + Some scripts from daskucsd (condor_utils.py, utils.py, condor_executable_jobqueue.sh, cachepreload.py) are copied to this repo
    + If there is a version conflict, use the latest from daskucsd and you might be careful to sort out package dependencies 
- Change daskworkerenv2.tar.gz in condor_utils.py and condor_executable_jobqueue.sh to whatever name you have when creating environment package following steps in daskucsd readme
- If you want to use these notebooks and scripts with condor workers, be careful one needs to supply local scripts in "input_files" in make_htcondor_cluster function from condor_utils.py 

# Other needed packages

- https://github.com/aminnj/yahist
