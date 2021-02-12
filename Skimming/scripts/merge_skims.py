import os
import glob
import argparse

import sys
sys.path.append("../../Utils/")
import parallel_utils

"""
This script gets a list of dirs of skimmed nanoAODs, identified by a wildcard,
and merges them into skims of a specified size.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--wildcard",
    help = "wildcard to grab skim dirs",
    type = str
)
parser.add_argument(
    "--input_dir",
    help = "path to input directory",
    type = str,
    default = "/hadoop/cms/store/user/legianni/ProjectMetis/"
)
parser.add_argument(
    "--output_dir",
    help = "output directory for merged skims",
    type = str,
    default = "/home/users/snt/Hgg/"
)
parser.add_argument(
    "--target_size",
    help = "target size of each merged skim (in GB)",
    type = float,
    default = 2.
)
parser.add_argument(
    "--nCores",
    help = "number of cores to use for hadding",
    type = int,
    default = 4
)
parser.add_argument(
    "--debug",
    help = "debug",
    type = int,
    default = 0
)
args = parser.parse_args()

### Helper functions ###
def get_size(file): 
    """
    Return file size in GB
    """
    size_bytes = os.path.getsize(file)
    size_gb = float(size_bytes) / (1024. * 1024. * 1024.)
    return size_gb

def split_files(files, file_size_map, target_size):
    map = { 1 : [] }
    current_size = 0
    idx = 1
    for file in files:
        current_size += file_size_map[file]
        if current_size > target_size:
            idx += 1
            current_size = file_size_map[file]
            map[idx] = []
        map[idx].append(file)
    return map    

def merge_files(file_map, output_dir):
    commands = []
    for idx, files in file_map.items():
        master = target_dir + "/merged_nanoAOD_skim_%d.root" % idx
        inputs = ""
        for file in files:
            inputs += file + " "

        command = "hadd -fk -k %s %s" % (master, inputs)
        commands.append(command)
    return commands

### Main script ###
if args.debug > 0:
    print("[merge_skims.py] Running with options: ", args)

directories = glob.glob(args.input_dir + args.wildcard)

if args.debug > 0:
    print("[merge_skims.py] Merging skims from the following directories: ")
    for dir in directories:
        print(dir)

command_list = []
for dir in directories:
    files = glob.glob(dir + "/*.root")

    target_dir = dir.replace(args.input_dir, args.output_dir)
    if not os.path.exists(target_dir):
        os.system("mkdir %s" % target_dir)

    file_size_map = {}
    total_size = 0

    for file in files:
        size = get_size(file)
        file_size_map[file] = size
        total_size += size

    file_map = split_files(files, file_size_map, args.target_size)

    if args.debug > 0:
        print("[merge_skims.py] Merging %d files of total size %.2f GB from directory %s into %d files in directory %s." % (len(files), size, dir, len(file_map.keys()), target_dir))
    
    command_list += merge_files(file_map, args.output_dir)

parallel_utils.submit_jobs(command_list, args.nCores)
