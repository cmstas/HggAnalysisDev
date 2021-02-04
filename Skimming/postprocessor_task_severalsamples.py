import sys, os
import time
import itertools
import numpy

import argparse

from metis.Sample import DirectorySample
from metis.CondorTask import CondorTask
from metis.StatsParser import StatsParser

from samples import *

print mc17
print mc16 
print mc18


exec_path = "exec_postproc.sh"
tar_path = "../rel2.tar.gz"
hadoop_path = ""


from tosumbit import tosubmit as a


for key in a:
    
    sample = DirectorySample(dataset = key, location ="/hadoop/cms/store/user/hmei/nanoaod_runII/HHggtautau/"+a[key] )

    files=[f.name for f in sample.get_files()]

    print "/hadoop/cms/store/user/hmei/nanoaod_runII/HHggtautau/"+a[key]

    #decide the type of job
    print (a[key] in mc16)
    print (a[key] in mc17)
    print (a[key] in mc18)
    print (a[key] in data16)
    print (a[key] in data17)
    print (a[key] in data18)

    output_name="test_nanoaodSkim.root"
    job_tag="___v4"
    job_args="1"
    
    if a[key] in mc18:
        job_args="mc18"
    elif a[key] in mc17:
        job_args="mc17" 
    elif a[key] in mc16:
        job_args="mc16" 
    elif a[key] in data18:
        job_args="data18"
    elif a[key] in data17:
        job_args="data17" 
    elif a[key] in data16:
        job_args="data16" 
    else:
        quit()
    print job_args

    # metis task
    # takes a tarball of the cmssw release and runs the job on a node (everything specified in the executable at exec_path
    task = CondorTask(
                sample = sample,
                open_dataset = False,
                flush = True,
                files_per_output = 20,
                #files_per_output = info["fpo"] i.e. can be stup by file
                output_name = output_name,
                tag = job_tag,
                cmssw_version = "CMSSW_10_2_22", # doesn't do anything
                arguments = job_args,
                executable = exec_path,
                tarfile = tar_path,
                condor_submit_params = {"sites" : "T2_US_UCSD","container":"/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7-m20201010"}

                )

    attrs = vars(task)
    
    # check attrs
    print(', '.join("%s: %s" % item for item in attrs.items()))

    task.process()

    total_summary = {}

    total_summary[task.get_sample().get_datasetname()] = task.get_task_summary()

    # Web dashboard
    StatsParser(data=total_summary, webdir="~/public_html/v4/").do()
    os.system("chmod -R 755 ~/public_html/v4/")
    
    print("Sleeping 10seconds ...")
    time.sleep(10)

