#! /usr/bin/bash

base_path=/home/users/iareed/HiggsDNA/Full_Samples_21Jun23/fixed_dijet_dummies

for file in $base_path/scored_SM/*
do
    out_dir=scored_M250
    echo "Zipping scores for $file"
    python zip_mva_scores.py --input "$file" --mvas "output/2HDM_M250_all_decays.json,output/2HDM_M300_all_decays.json,output/2HDM_M350_all_decays.json" --names "2HDM_M250_scores,2HDM_M300_scores,2HDM_M350_scores" --output "${file}"
done

