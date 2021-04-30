## Introduction 

`HggAnalysisDev` is a repository of tools for fast and flexible development of H->gg analyses.
The main components are:
1. **Preselection**: loop over nanoAODs and write events to a `pandas` dataframe, make plots and tables from these dataframes
2. **MVA Training & Evaluation**: starting from output of 1 (`pandas` dataframe), train and evaluate BDTs (using `xgboost`) and deep neural networks (using `tensorflow` and `keras`), plot performance metrics, and zip MVA scores back into dataframes.
3. **Signal Region Optimization**: scan a variety of cuts on one or more variables (typically MVAs) to define signal regions. Within each signal region, fit `m_gg` distribution to create signal and background (non-resonant and resonant) models, and evaluate a figure of merit (significance, upper limit, etc) in these signal regions.

**Note**: step 3 currently relies on old code from the ttH (HIG-19-013/HIG-19-015) and FCNC (TOP-20-007) analyses which has `CMSSW` and `combine` dependencies. Planned to be updated to a pure-python implementation using `zfit` and `hepstats`.

## Tutorial: ttH Leptonic analysis
This provides a walkthrough for developing a new H->gg analysis from end-to-end. It assumes you already have custom nanoAOD files with the diphoton preselection applied (see Hgg common tools AN-2019/149) and relevant photon branches for performing the diphoton preselection (these are not present in default nanoAOD at the time of writing).

As an example, we will develop an analysis for measuring ttH (H->gg) in the leptonic (semi-leptonic and di-leptonic decays of ttbar) channel.

1. Identify relevant samples: start by constructing a `json` file with all of the relevant samples for your analysis.
   For ttH, we can start with signal samples (ttH), data, and a couple relevant backgrounds: gamma + jets, diphoton + jets, and ttbar + 0-2 photons.
   The `json` file will have an entry for each sample you want to run on. We can construct it like this:

```
{
    "ttH" : {
        "resonant" : true,
        "fpo" : 10,
        "process_id" : -1,
        "2016" : {
            "paths" : ["/hadoop/cms/store/user/legianni/skimNano-Hggselection/ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_private_mc17/"],
            "metadata" : { "xs" : 0.001151117 }
        },
        "2017" : {
            "paths" : ["/hadoop/cms/store/user/legianni/skimNano-Hggselection/ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_private_mc17/"],
            "metadata" : { "xs" : 0.001151117 }
        },
        "2018" : {
            "paths" : ["/hadoop/cms/store/user/legianni/skimNano-Hggselection/ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_private_mc18/"],
            "metadata" : { "xs" : 0.001151117 }
        }
    },
    "Data" : {
    ...
    }
}
```
 
    The full `json` file is available [here](https://github.com/cmstas/HggAnalysisDev/blob/3d00f19482a93fa6bf824c32d54bb3e9cfe0bad7/Preselection/data/samples_ttH.json).

2. Calculate `scale1fb` and other relevant metadata for the samples. This can be done using the script `Preselection/scripts/scale1fb.py`:
```
python scale1fb.py --input <path_to_above_json> --output "data/samples_and_scale1fb.json" --debug 1
```

3. 
