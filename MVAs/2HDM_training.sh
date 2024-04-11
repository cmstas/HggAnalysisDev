#! /usr/bin/bash

for mass in 250 275 300 325 350 
do
    echo "Training for $mass"

    sed -i "3,5 s/dummy/${mass}/g" plot_mva.json
    python prep.py --input "/home/users/iareed/HiggsDNA/Full_Samples_with_tH_fixed_bf/merged_nominal.parquet" --config "data/HiggsDNA_2HDM_AN7_22Sep23_with_tH.json" --output "output/2HDM_M${mass}_05Apr24_with_tH.hdf5" > 2HDM_M${mass}_tag.log
    sed -i "3,5 s/${mass}/dummy/g" plot_mva.json
done

