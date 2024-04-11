#! /usr/bin/bash


for mass in 500 550 600 650 700 750 800 850 900 950 1000 1100 1200 1300 1400 1500
do
    echo "Converting files for Tprime $mass"
    python convert_awkward_to_numpy.py --input "output/Tprime_M${mass}_28Feb23_df.parquet"
done

