import json
import numpy as np

# How many limits to pull results for, starting with the best
depth = 3
# Location of output files from optimization script
in_dir = 'optimization_results/'
# Start of each file name, separate to make it easier to just add tag, assumes same optimization
base = 'guided_optimizer_results_HH_FCNC_Leptonic_'
# Tags given to optimizations that you want to find the best limits of
tags = [
        #'ttHH_02Aug22',
        '2HDM_M250_26Jul22',
        '2HDM_M250_02Aug22',
        '2HDM_M250_02Aug22_v2',
        '2HDM_M250_11Aug22',
        '2HDM_M250_11Aug22_broken_cand',
        #'2HDM_M300_29Jul22',
        #'2HDM_M300_02Aug22',
        #'2HDM_M300_02Aug22_check',
        #'2HDM_M300_02Aug22_v2',
        #'2HDM_M350_26Jul22',
        #'2HDM_M350_29Jul22',
        #'2HDM_M350_02Aug22',

        #'tagger_test'
        ]

def limit_skimmer(in_dir,base,tag):
    with open(in_dir+base+tag+'.json', 'r') as f_in:
        results = json.load(f_in)

    limits = np.array([])
    sr1 = np.array([])
    sr2 = np.array([])
    yields = np.array([])
    spreads = np.array([])

    for guess in results['1d']['2']['guided']['exp_lim']:
        if guess['disqualified'] == "True":
            continue
        limits = np.append(limits, guess['exp_lim'][0])
        sr1 = np.append(sr1, guess['selection'][0][-6:])
        sr2 = np.append(sr2, guess['selection'][1][13:21])
        yields = np.append(yields, guess['yields'])
        spreads = np.append(spreads, guess['exp_lim'])

    # Sort by limits to get position
    best_pos = np.argsort(limits)
    print('For analysis {}, the best {} results are'.format(tag,depth))
    print('Limits: ', limits[best_pos][:depth])
    print('SR1 edges: ', sr1[best_pos][:depth])
    print('SR2 edges: ', sr2[best_pos][:depth])

for tag in tags:
    print('')
    limit_skimmer(in_dir,base,tag)
    print('')
    print('-----------------------------------')

