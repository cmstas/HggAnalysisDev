import json

in_dir = '/home/users/iareed/HggAnalysisDev/ttH_SR_Optimization/optimization_results/'
base = 'guided_optimizer_results_HH_FCNC_Leptonic_'
tags = [
       'ttHH_02Aug22'
	#'ttHH_04Jul22',
        #'2HDM_03Jul22',
        #'2HDM_M300_29Jul22',
        #'ttHH_02Aug22',
        #'2HDM_M250_02Aug22',
        #'2HDM_M250_02Aug22_v2',
        #'2HDM_M300_02Aug22',
        #'2HDM_M300_02Aug22_v2',
        #'2HDM_M300_02Aug22_check',
        #'Tprime_08Aug22',
        #'Tprime_09Aug22_no_lep_no_tau',
        #'2HDM_M350_02Aug22'
        ]

def limit_skimmer(in_dir,base,tag):
    with open(in_dir+base+tag+'.json', 'r') as f_in:
        results = json.load(f_in)

    best_lim = 999
    best_selection = ['0','0']
    best_yields = -999
    best_spread = -999

    for guess in results['1d']['2']['guided']['exp_lim']:
        if guess['disqualified'] == "True":
            continue
        if guess['exp_lim'][0] < best_lim:
            best_lim = guess['exp_lim'][0]
            best_spread = guess['exp_lim']
            best_selection = guess['selection']
            best_yields = guess['yields']

    print('For analysis: {}, the best limit was: {}, with selections, {}'.format(tag,best_lim,best_selection))
    print('Spread: ', best_spread)
    print('It\'s yields were: ', best_yields)

for tag in tags:
    limit_skimmer(in_dir,base,tag)
    print('-----------------------------------')
    print('')
