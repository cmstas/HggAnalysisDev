#! /usr/bin/bash

base_path=/home/users/iareed/HiggsDNA/BSM_13Oct22

for file in $base_path/merged_backups/*
do
    out_dir=fixed_weight
    echo "Reweighting 2HDM for $file"
    sed -i "s#file_in#$file#g" weight_central_updater_batch.py
    sed -i "s#file_out#${file/merged_backup/$out_dir}#g" weight_central_updater_batch.py

    python weight_central_updater_batch.py

    sed -i "s#$file#file_in#g" weight_central_updater_batch.py
    sed -i "s#${file/merged_backup/$out_dir}#file_out#g" weight_central_updater_batch.py

done

