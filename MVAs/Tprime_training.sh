#! /usr/bin/bash

for mass in 500 550 600 650 700 750 800 850 900 950 1000 1100 1200 1300 1400 1500
do
    echo "Training for $mass"

    sed -i "3,5 s/dummy/${mass}/g" plot_mva.json
    python prep.py --input "/home/users/iareed/HiggsDNA/Full_Samples_with_tH_fixed_bf/merged_nominal.parquet" --config "data/HiggsDNA_Tprime_AN7_22Sep23_with_tH.json" --output "output/Tprime_M${mass}_05Apr24_with_tH.hdf5" > Tprime_M${mass}_tag.log
    sed -i "3,5 s/${mass}/dummy/g" plot_mva.json
done

