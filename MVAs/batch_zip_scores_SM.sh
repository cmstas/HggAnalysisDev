#! /usr/bin/bash

base_path=/home/users/iareed/HiggsDNA/Full_Samples_with_tH_with_systematics

for file in $base_path/merged_*.parquet
do
    echo "Zipping scores for $file"
    python zip_mva_scores.py --input "$file" --mvas "output/SM_with_TH_20240212_fixed_bf.json" --output "${file}"
done

