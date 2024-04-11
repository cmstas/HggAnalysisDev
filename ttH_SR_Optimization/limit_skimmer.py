import json
import numpy as np

# How many limits to pull results for, starting with the best
depth = 3
# Location of output files from optimization script
in_dir = 'optimization_results/'
#in_dir = 'Giacomo_results/'
# Start of each file name, separate to make it easier to just add tag, assumes same optimization
#base = 'guided_optimizer_results_ttHH_FCNC_Leptonic_'
base = 'guided_optimizer_results_HH_FCNC_Leptonic_'
# Tags given to optimizations that you want to find the best limits of
tags = [
        #'SM_23_Sep22_full',
        'SM_22Sep23_fixed_dijet',
        'tH_inflated_16',
        'SM_with_tH_in_training_fixed_bf',

        #'global_SM_test_14Dec22',
        #'SM_26Jun23',

        #'ttHH_with_impact_nominal',
        #'ttHH_no_impact_nominal',

        #'ttHH_no_ditau',

        #'eta_0_4',
        #'eta_0_5',
        #'eta_0_6'

        #'2HDM_M275_using_M250_score',
        #'2HDM_M275_using_M275_score',
        #'2HDM_M275_using_M300_score',

        #'2HDM_M325_using_M300_score',
        #'2HDM_M325_using_M325_score',
        #'2HDM_M325_using_M350_score',


        #'2HDM_M250_all_decays',
        #'2HDM_M300_all_decays',
        #'2HDM_M350_all_decays',
        #'2HDM_M250_bb_only',
        #'2HDM_M250_bb_only_fixed_weight',
        #'2HDM_M250_fixed_weights',
        #'2HDM_M250_data_check',
        #'2HDM_M250_data_div3',
        #'2HDM_M250_no_triple',
        #'2HDM_M250_fixed_data_weight',
        #'2HDM_M250_29Sep23_fixed_dijet',
        #'2HDM_M300_22Sep23_fixed_dijet',
        #'2HDM_M350_22Sep23_fixed_dijet',
        #'2HDM_M250_fixed_data_weight_modified_selection',
        #'2HDM_M300_fixed_weights',
        #'2HDM_M350_fixed_weights',
        #'2HDM_M300_03Oct23_fixed_scores',
        #'Tprime_M500_28Feb23',
        #'Tprime_M550_28Feb23',
        #'Tprime_M600_28Feb23',
        #'Tprime_M650_28Feb23',
        #'Tprime_M700_28Feb23',
        #'Tprime_M750_28Feb23',
        #'Tprime_M800_28Feb23',
        #'Tprime_M850_28Feb23',
        #'Tprime_M900_28Feb23',
        #'Tprime_M950_28Feb23',
        #'Tprime_M1000_28Feb23',
        #'Tprime_M1100_28Feb23',
        #'Tprime_M1200_28Feb23',
        #'Tprime_M1300_28Feb23',
        #'Tprime_M1400_28Feb23',
        #'Tprime_M1500_28Feb23',
        #'Tprime_group_score_test_28Feb23'
        #'SM_num_srs_comparison_1_bin',
        #'SM_num_srs_comparison_2_bin',
        #'SM_num_srs_comparison_3_bin',
        #'SM_num_srs_comparison_3_bin_v_two',
        #'SM_num_srs_comparison_4_bin'

        #'Tprime_M1500_04Jan23',
        #'Tprime_M1500_25Jan23',


        #'ttHH_all_channels_26Jan23',
        #'Tprime_M500_07Apr23_test_07Apr23',
        #'Tprime_M500_27Apr23',
        #'Tprime_M550_27Apr23',
        #'Tprime_M600_27Apr23',
        #'Tprime_M650_27Apr23',
        #'Tprime_M700_27Apr23',
        #'Tprime_M750_27Apr23',
        #'Tprime_M800_27Apr23',
        #'Tprime_M850_27Apr23',
        #'Tprime_M900_27Apr23',
        #'Tprime_M950_27Apr23',
        #'Tprime_M1000_27Apr23',
        #'Tprime_M1100_27Apr23',
        #'Tprime_M1200_27Apr23',
        #'Tprime_M1300_27Apr23',
        #'Tprime_M1400_27Apr23',
        #'Tprime_M1500_27Apr23',
        #'SM_28Apr23_no_lepton_mass',
        #'ttHH_no_impact_31Jan2',
        #'2HDM_M250_01May23_four_body',
        #'2HDM_M300_04May23_four_body',
        #'2HDM_M350_04May23_four_body',
        #'Tprime_M1000_27Apr23_penalty',
        #'Tprime_M1100_27Apr23_penalty',
        #'Tprime_M1200_27Apr23_penalty',
        #'Tprime_M1300_27Apr23_penalty',
        #'Tprime_M1400_27Apr23_penalty',
        #'Tprime_M1500_27Apr23_penalty'

        #'Tprime_M500_02Oct23',
        #'Tprime_M550_02Oct23',
        #'Tprime_M600_02Oct23',
        #'Tprime_M650_02Oct23',
        #'Tprime_M700_02Oct23',
        #'Tprime_M750_02Oct23',
        #'Tprime_M800_02Oct23',
        #'Tprime_M850_02Oct23',
        #'Tprime_M900_02Oct23',
        #'Tprime_M950_02Oct23',
        #'Tprime_M1000_02Oct23',
        #'Tprime_M1100_02Oct23',
        #'Tprime_M1200_02Oct23',
        #'Tprime_M1300_02Oct23',
        #'Tprime_M1400_02Oct23',
        #'Tprime_M1500_02Oct23',
        'Tprime_M500_with_tH',        
        'Tprime_M550_with_tH',        
        'Tprime_M600_with_tH',        
        'Tprime_M650_with_tH',        
        'Tprime_M700_with_tH',        
        'Tprime_M750_with_tH',        
        'Tprime_M800_with_tH',        
        'Tprime_M850_with_tH',        
        'Tprime_M900_with_tH',        
        'Tprime_M950_with_tH',        
        'Tprime_M1000_with_tH',        
        'Tprime_M1100_with_tH',        
        'Tprime_M1200_with_tH',        
        'Tprime_M1300_with_tH',        
        'Tprime_M1400_with_tH',        
        'Tprime_M1500_with_tH',        
        ]

def limit_skimmer(in_dir,base,tag,save_list):
    with open(in_dir+base+tag+'.json', 'r') as f_in:
        results = json.load(f_in)

    limits = np.array([])
    sr1 = np.array([])
    sr2 = np.array([])
    idxs = np.array([])
    yields = np.array([])
    data_sr1 = np.array([])
    data_sr2 = np.array([])
    spreads = np.array([])

#    for i in range(5):
#        if str(i) in tag:
#            n_bins=str(i)
    n_bins='2'
    for guess in results['1d'][n_bins]['guided']['exp_lim']:
        if guess['disqualified'] == "True":
            continue
        if guess['exp_lim'][0]<18:
            continue
        limits = np.append(limits, guess['exp_lim'][0])
        sr1 = np.append(sr1, guess['selection'][0][-6:])
        ping = guess['selection'][1].find(">= ")
        sr2 = np.append(sr2, guess['selection'][1][ping+3:ping+11])
        idxs = np.append(idxs, guess['idx'])
        yields = np.append(yields, guess['yields'])
        data_sr1 = np.append(data_sr1, guess['yields']['Bin_0']['data_raw'])
        data_sr2 = np.append(data_sr2, guess['yields']['Bin_1']['data_raw'])
        spreads = np.append(spreads, guess['exp_lim'])

    # Sort by limits to get position
    best_pos = np.argsort(limits)
    print('For analysis {}, the best {} results are'.format(tag,depth))
    print('Limits: ', limits[best_pos][:depth])
    print('SR1 edges: ', sr1[best_pos][:depth])
    print('Data in SR1: ', data_sr1[best_pos][:depth])
    print('SR2 edges: ', sr2[best_pos][:depth])
    print('Data in SR2: ', data_sr2[best_pos][:depth])
    print('idx: ', idxs[best_pos][:depth])

    #save_list['Tag'].append(tag)
    #save_list['Limit'].append(str(limits[best_pos][0]))
    #save_list['SR1'].append(sr1[best_pos][0])
    #save_list['SR2'].append(sr2[best_pos][0])

save_list = {'Tag':[], 'Limit':[], 'SR1':[], 'SR2':[]}
for tag in tags:
    print('')
    limit_skimmer(in_dir,base,tag,save_list)
    print('')
    print('-----------------------------------')

#print(save_list)
#out_format = json.dumps(save_list, indent=4)
#with open('Tprime_list.json','w') as outfile:
#    outfile.write(out_format)
