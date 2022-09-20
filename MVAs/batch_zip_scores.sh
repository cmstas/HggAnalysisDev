#! /usr/bin/bash

base_path=/home/users/iareed/HiggsDNA/SM_09Sep22

for file in $base_path/merged_backups/*
do
    out_dir=scored_dataframes
    echo "Zipping scores for $file"
    python zip_mva_scores.py --input "$file" --mvas "output/tagger_test.json" --output "${file/merged_backups/$out_dir}"
done

