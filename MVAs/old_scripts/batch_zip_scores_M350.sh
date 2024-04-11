#! /usr/bin/bash

base_path=/home/users/iareed/HiggsDNA/BSM_13Oct22

for file in $base_path/fixed_weights/*
do
    out_dir=scored_M350
    echo "Zipping scores for $file"
    python zip_mva_scores.py --input "$file" --mvas "output/2HDM_M350_all_decays.json" --output "${file/fixed_weights/$out_dir}"
done

