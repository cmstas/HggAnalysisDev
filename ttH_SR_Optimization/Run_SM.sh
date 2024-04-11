#! /usr/bin/bash

python optimize_srs_hh.py --file "SM_xxxxx.root" --proc_ids "/home/users/iareed/HiggsDNA/Full_Samples_with_tH_fixed_bf/summary.json" --tag "SM_xxxxxx_with_tH" --coupling "HH" --nCores 10 --bins "2" --metric "upper limit" --mvas "SM_mva_score" 
