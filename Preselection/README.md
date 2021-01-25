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
- Change daskworkerenv2.tar.gz in condor_utils.py to whatever name you have when creating environment package following steps in daskucsd readme
- If you want to use these notebooks and scripts with condor workers, be careful one needs to supply local scripts in "input_files" in make_htcondor_cluster function from condor_utils.py 

# Other needed packages

- https://github.com/aminnj/yahist
