#! /usr/bin/bash

for mass in 250 275 300 325 350
do
    echo "Optimizing for $mass"
    sed -i "126 s/dummy/${mass}/g" guided_optimizer_hh.py
    python optimize_srs_hh.py --file "2HDM_xxxxx.root" --proc_ids "/home/users/iareed/HiggsDNA/Full_Samples_with_tH_fixed_bf/summary.json" --tag "2HDM_M${mass}_with_tH" --coupling "HH" --nCores 10 --bins "2" --metric "upper limit" --mvas "2HDM_M${mass}_score" 
    sed -i "126 s/${mass}/dummy/g" guided_optimizer_hh.py
done
