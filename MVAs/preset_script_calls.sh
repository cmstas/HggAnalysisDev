#! /usr/bin/bash

#TODO: Note, these commands are useful mostly the SM/nominals in isolation. Use the batch_zip_scores_XXXX.sh for dealing with all the systematic variation files
#TODO: Note, you can use the structures of those files when dealing with the nominal for them if you need to optimize

#input: absolute path to the input file for training
#config: relative path to the training configuration file
#output: tag to be used for the training, .hdf5 needed for legacy reasons
python prep.py --input "/home/users/iareed/HiggsDNA/pre_app_condor/merged_nominal.parquet" --config "data/HiggsDNA_ttHH_with_tH.json" --output "pre_app_20240427.hdf5"

#TODO: Use the next two if running the optimization
#input: absolute path of the file to score
#mvas: relative path to the training result json
#names: name to use in the parquet
#output: location and name to save the output file
python zip_mva_scores.py --input "/home/users/iareed/HiggsDNA/pre_app_condor/merged_nominal.parquet" --mvas "output/pre_app_20240427.json" --names "SM_mva_score" --output "pre_app_20240427.parquet"

#input: path to parquet to be converted to the numpy file
python convert_awkward_to_numpy.py --input "pre_app_20240427.parquet"

#TODO: When scoring all the systematic variations, use the batch_zip_scores_XXXX.sh files
#TODO: For optimization, cd ../ttH_SR_Optimization

#After the batch scoreing, cd ../../HggNanoAnalysis/scripts
