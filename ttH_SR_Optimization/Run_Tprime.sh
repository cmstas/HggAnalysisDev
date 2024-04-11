#! /usr/bin/bash

for mass in 500 550 600 650 700 750 800 850 900 950 1000 1100 1200 1300 1400 1500
do
    echo "Optimizing for $mass"
    sed -i "133 s/dummy/${mass}/g" guided_optimizer_hh.py
    python optimize_srs_hh.py --file "Tprime_with_tH.root" --proc_ids "/home/users/iareed/HiggsDNA/Full_Samples_with_tH_fixed_bf/summary.json" --tag "Tprime_M${mass}_with_tH" --coupling "HH" --nCores 10 --bins "2" --metric "upper limit" --mvas "Tprime_M${mass}_score" 
    sed -i "133 s/${mass}/dummy/g" guided_optimizer_hh.py
done
