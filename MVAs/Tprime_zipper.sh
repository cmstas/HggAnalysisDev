#! /usr/bin/bash

#echo "Zipping scores for SM"
#python zip_mva_scores.py --input "/home/users/iareed/HiggsDNA/EWK_with_others_22Jun23/merged_nominal.parquet" --mvas "output/SM_28Apr23_no_lepton_mass.json" --names "mva_score_SM" --output "output/EWK_scored_df.parquet"
#
#for mass in 600 700 900 1400 1500
#do
#    echo "Zipping scores for M$mass"
#    python zip_mva_scores.py --input "output/EWK_scored_df.parquet" --mvas "output/Tprime_M${mass}_27Apr23.json" --names "mva_score_Tprime_M${mass}" --output "output/EWK_scored_df.parquet"
#done

python zip_mva_scores.py --input "/home/users/iareed/HiggsDNA/Full_Samples_with_tH_fixed_bf/merged_nominal.parquet" --mvas "output/Tprime_M500_05Apr24_with_tH.json,output/Tprime_M550_05Apr24_with_tH.json,output/Tprime_M600_05Apr24_with_tH.json,output/Tprime_M650_05Apr24_with_tH.json,output/Tprime_M700_05Apr24_with_tH.json,output/Tprime_M750_05Apr24_with_tH.json,output/Tprime_M800_05Apr24_with_tH.json,output/Tprime_M850_05Apr24_with_tH.json,output/Tprime_M900_05Apr24_with_tH.json,output/Tprime_M950_05Apr24_with_tH.json,output/Tprime_M1000_05Apr24_with_tH.json,output/Tprime_M1100_05Apr24_with_tH.json,output/Tprime_M1200_05Apr24_with_tH.json,output/Tprime_M1300_05Apr24_with_tH.json,output/Tprime_M1400_05Apr24_with_tH.json,output/Tprime_M1500_05Apr24_with_tH.json" --names "Tprime_M500_score,Tprime_M550_score,Tprime_M600_score,Tprime_M650_score,Tprime_M700_score,Tprime_M750_score,Tprime_M800_score,Tprime_M850_score,Tprime_M900_score,Tprime_M950_score,Tprime_M1000_score,Tprime_M1100_score,Tprime_M1200_score,Tprime_M1300_score,Tprime_M1400_score,Tprime_M1500_score" --output "/home/users/iareed/HggAnalysisDev/MVAs/output/Tprime_with_tH.parquet"
