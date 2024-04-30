#! /usr/bin/bash

source setup.sh

#input: relative path to the numpy file made in the MVAs with all the scores
python convert_awkward_to_numpy.py --input "../MVAs/output/tag.npz"

#Use the respective Run_XXXX.sh to configure and process the optimization

#To extract the valid limits, add the tag to limit_skimmer.py
