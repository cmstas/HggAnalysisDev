#!/usr/bin/env python

import os
import tempfile
import argparse

from dask_jobqueue.htcondor import HTCondorJob, HTCondorCluster, quote_environment

BASEDIR = os.path.dirname(os.path.realpath(__file__))

def submit_workers(scheduler_url, dry_run=False, num_workers=1, blacklisted_machines=[], memory=4000, disk=20000, whitelisted_machines=[]):

    template = """
universe                = vanilla
should_transfer_files   = YES
when_to_transfer_output = ON_EXIT_OR_EVICT
transfer_output_files = ""
Transfer_Executable     = True
transfer_input_files    = utils.py,cachepreload.py,daskworkerenv2.tar.gz
output                  = logs/1e.$(Cluster).$(Process).out
error                   = logs/1e.$(Cluster).$(Process).err
log                     = logs/$(Cluster).log
executable              = condor_executable.sh
RequestCpus = 1
RequestMemory = {memory}
RequestDisk = {disk}
x509userproxy={proxy}
+DESIRED_Sites="T2_US_UCSD"
+SingularityImage="/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7-m20201010"
JobBatchName = "daskworker"
Requirements = ((HAS_SINGULARITY=?=True) && (HAS_CVMFS_cms_cern_ch =?= true) && {extra_requirements})
Arguments = {scheduler_url}
queue {num_workers}
    """

    extra_requirements = "True"
    if blacklisted_machines:
        extra_requirements = " && ".join(map(lambda x: '(TARGET.Machine != "{0}")'.format(x),blacklisted_machines))
    if whitelisted_machines:
        extra_requirements = " || ".join(map(lambda x: '(TARGET.Machine == "{0}")'.format(x),whitelisted_machines))

    content = template.format(
            extra_requirements=extra_requirements,
            num_workers=num_workers,
            scheduler_url=scheduler_url,
            proxy="/tmp/x509up_u{0}".format(os.getuid()),
            memory=memory,
            disk=disk,
            )

    f = tempfile.NamedTemporaryFile(delete=False)
    filename = f.name
    f.write(content.encode())
    f.close()

    if dry_run:
        print(content)
    else:
        os.system("mkdir -p logs/")
        os.system("condor_submit " + filename)

    # f.unlink(filename)

class UCSDHTCondorJob(HTCondorJob):

    # DEFAULT: submit_command = "condor_submit -queue 1 -file"
    # -file doesn't exist for this condor version, and if the submit file name gets put
    # right after -queue 1, then condor thinks it's an argument to -queue, hence the -debug
    # sandwiched in between
    # NO longer need to override `submit_command` after https://github.com/dask/dask-jobqueue/commit/c1e0a21a32d909edaf8fc1afb5a1d49b43f5bc33#diff-a384f2a64350f53bcec5f8a223f5d1f62d32cd1f6146febf1cee3400c548d284
    # submit_command = "condor_submit -queue 1 -debug"
    executable = os.path.join(BASEDIR, "condor_executable_jobqueue.sh")
    config_name = "htcondor"

    def job_script(self):
        """ Construct a job submission script """
        quoted_environment = quote_environment(self.env_dict)
        job_header_lines = "\n".join(
            "%s = %s" % (k, v) for k, v in self.job_header_dict.items()
        )
        return self._script_template % {
            "shebang": self.shebang,
            "job_header": job_header_lines,
            "quoted_environment": quoted_environment,
            "quoted_arguments": self._command_template,
            "executable": self.executable,
        }

class UCSDHTCondorCluster(HTCondorCluster):
    job_cls = UCSDHTCondorJob
    config_name = "htcondor"

def make_sure_exists(path, make=False):
    if not os.path.exists(path):
        if not make:
            raise Exception("Input {} doesn't exist".format(path))
        else:
            os.system("mkdir -p {}".format(path))


def make_htcondor_cluster(
        disk = "8GB",
        memory = "4GB",
        cores = 1,
        local=False,
        dashboard_address=8787,
        ):

    input_files = [os.path.join(BASEDIR, x) for x in ["utils.py","cachepreload.py","daskworkerenv2.tar.gz", "event_selector.py", "looper_utils.py", "make_plots.py"]]
    log_directory = os.path.join(BASEDIR, "logs/")
    proxy_file = "/tmp/x509up_u{0}".format(os.getuid())

    [make_sure_exists(p) for p in input_files + [proxy_file]]
    make_sure_exists(log_directory, make=True)

    blacklisted_machines = ["cabinet-11-11-2.t2.ucsd.edu", "cabinet-11-11-6.t2.ucsd.edu", "cabinet-0-0-23.t2.ucsd.edu", "cabinet-0-0-30.t2.ucsd.edu", "cabinet-11-11-0.t2.ucsd.edu", "cabinet-0-0-20.t2.ucsd.edu", "cabinet-0-0-22.t2.ucsd.edu", "cabinet-0-0-21.t2.ucsd.edu", "cabinet-0-0-29.t2.ucsd.edu", "cabinet-11-11-9.t2.ucsd.edu", "cabinet-11-11-3.t2.ucsd.edu", "cabinet-0-0-31.t2.ucsd.edu", "cabinet-0-0-28.t2.ucsd.edu", "cabinet-3-3-2.t2.ucsd.edu"]


    params = {
            "disk": disk,
            "memory": memory,
            "cores": cores,
            "log_directory": log_directory,
            "scheduler_options": {
                "dashboard_address": dashboard_address,
                },
            "python": "python",
            "job_extra":  {
                "should_transfer_files": "YES",
                "when_to_transfer_output": "ON_EXIT_OR_EVICT",
                "transfer_output_files": "",
                "Transfer_Executable": "True",
                "transfer_input_files": ",".join(input_files),
                "JobBatchName": '"daskworker"',
                "x509userproxy": proxy_file,
                "+SingularityImage":'"/cvmfs/singularity.opensciencegrid.org/bbockelm/cms:rhel7"',
                "Stream_Output": False,
                "Stream_Error": False,
                "+DESIRED_Sites":'"T2_US_UCSD"',
                "Requirements": '((HAS_SINGULARITY=?=True) && (HAS_CVMFS_cms_cern_ch =?= true) && (TARGET.Machine != "sdsc-18.t2.ucsd.edu") && (TARGET.Machine != "sdsc-20.t2.ucsd.edu") && (TARGET.Machine != "cabinet-7-7-36.t2.ucsd.edu") && (TARGET.Machine != "cabinet-4-4-18.t2.ucsd.edu") && (TARGET.Machine != "cabinet-0-0-21.t2.ucsd.edu") && (TARGET.Machine != "cabinet-0-0-23.t2.ucsd.edu"))',
                },
            "extra": ["--preload", "cachepreload.py"],
            }

    params["job_extra"]['Requirements'] +=  " && " + " && ".join(map(lambda x: '(TARGET.Machine != "{0}")'.format(x),blacklisted_machines))

    if local:
        params["+DESIRED_Sites"] = '"UAF"'
        params["Requirements"] = ''

    cluster = UCSDHTCondorCluster(**params)
    return cluster

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--scheduler_url", help="scheduler url"
            "(if not specified, attempts to use the result of `from config import scheduler_URL`)", default="")
    parser.add_argument("-d", "--dry_run", help="echo submit file, but don't submit", action="store_true")
    parser.add_argument("-n", "--num_workers", help="number of workers", default=1, type=int)
    parser.add_argument("-b", "--blacklisted_machines", help="blacklisted machines", default=[
            # "sdsc-49.t2.ucsd.edu",
            # "sdsc-50.t2.ucsd.edu",
            # "sdsc-68.t2.ucsd.edu",
            # "cabinet-7-7-36.t2.ucsd.edu",
            # "cabinet-8-8-1.t2.ucsd.edu",
    ], action="append")
    parser.add_argument("-w", "--whitelisted_machines", help="whitelisted machines", default=[], action="append")
    args = parser.parse_args()

    submit_workers(args.scheduler_url, dry_run=args.dry_run, num_workers=args.num_workers, blacklisted_machines=args.blacklisted_machines, whitelisted_machines=args.whitelisted_machines)
