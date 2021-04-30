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

### Preselection
1) Identify relevant samples: start by constructing a `json` file with all of the relevant samples for your analysis.
   For ttH, we can start with signal samples (ttH), data, and a couple relevant backgrounds: gamma + jets, diphoton + jets, and ttbar + 0-2 photons.
   The `json` file will have an entry for each sample you want to run on. We can construct it like this:

```
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
```
 
    The full `json` file is available [here](https://github.com/cmstas/HggAnalysisDev/blob/3d00f19482a93fa6bf824c32d54bb3e9cfe0bad7/Preselection/data/samples_ttH.json).

2) Calculate `scale1fb` and other relevant metadata for the samples. This can be done using the script `Preselection/scripts/scale1fb.py`:

```
python scale1fb.py --input <path_to_above_json> --output "data/samples_and_scale1fb.json" --debug 1
```

3) Implement a preselection.
   This can be done by adding a function to `Preselection/selections/analysis_selections.py`:

```python
def tth_leptonic_preselection(events, photons, electrons, muons, jets, options, debug):
    """
    Performs tth leptonic preselection, requiring >= 1 lepton and >= 1 jet
    Assumes diphoton preselection has already been applied.
    Also calculates relevant event-level variables.
    """

    # The CutDiagnostics is an optional (but recommended) way to track the efficiencies of each cut you implement.
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : tth_leptonic_preselection]")

    # Many generic functions for selecting leptons, jets, etc are contained in various other files within `Preselection/selections`, as shown below.
    # Get number of electrons, muons
    selected_electrons = electrons[lepton_selections.select_electrons(events, photons, electrons, options, debug)]
    selected_muons = muons[lepton_selections.select_muons(events, photons, muons, options, debug)]

    n_electrons = awkward.num(selected_electrons)
    n_muons = awkward.num(selected_muons)
    n_leptons = n_electrons + n_muons

    # Get number of jets
    selected_jets = jets[jet_selections.select_jets(events, photons, selected_electrons, selected_muons, None, jets, options, debug)]
    n_jets = awkward.num(selected_jets)

    lep_cut = n_leptons >= 1
    jet_cut = n_jets >= 1

    all_cuts = lep_cut & jet_cut
    cut_diagnostics.add_cuts([lep_cut, jet_cut, all_cuts], ["N_leptons >= 1", "N_jets >= 1", "all"])

    # Keep only selected events
    selected_events = events[all_cuts]
    selected_photons = photons[all_cuts]
    selected_electrons = selected_electrons[all_cuts]
    selected_muons = selected_muons[all_cuts]
    selected_jets = selected_jets[all_cuts]

    # Calculate event-level variables
    selected_events = lepton_selections.set_electrons(selected_events, selected_electrons, debug)
    selected_events = lepton_selections.set_muons(selected_events, selected_muons, debug)
    selected_events = jet_selections.set_jets(selected_events, selected_jets, options, debug)

    return selected_events
```
 
   You next need to associate this function with a string so you can specify the ttH leptonic preselection from the command line.
   This is done in `Preselection/helpers/loop_helper.py`, in the `select_events` function [here](https://github.com/cmstas/HggAnalysisDev/blob/3d00f19482a93fa6bf824c32d54bb3e9cfe0bad7/Preselection/helpers/loop_helper.py#L225), like so:

```
elif self.selections == "ttH_LeptonicPresel":
    selected_events = analysis_selections.tth_leptonic_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Jet, options, self.debug)
```

4) Loop over samples and perform the preselection, writing events to a `pandas` dataframe.
   First we will need to construct an options `json` for the ttH leptonic preselection. An example is available [here](https://github.com/cmstas/HggAnalysisDev/blob/3d00f19482a93fa6bf824c32d54bb3e9cfe0bad7/Preselection/data/ttH_Leptonic.json).
   The important fields in this `json` are:
    - `"branches"` : list of branches to read from nanoAOD. Ensure that any branches that your code will access are specified here.
    - `"save_branches"` : list of branches to be written to the output dataframe. This could include branches that are read directly from nanoAOD, as well as variables that you might compute during your preselection. For example, we probably want to store things like the kinematics of selected leptons and jets in the preselection. If you add variables to save here, make sure they are either present in `"branches"` or computed somewhere in your code. [Here](https://github.com/cmstas/HggAnalysisDev/blob/3d00f19482a93fa6bf824c32d54bb3e9cfe0bad7/Preselection/selections/lepton_selections.py#L45-L63) is an example of adding branches to the events object in the looper. **NB**: the output dataframe is assumed to be flat. Any "awkward"-shaped arrays should be transformed into a flat structure, as in the example linked above (i.e. rather than save `electron_pt` as a vector for each event, we save `electron1_pt`, `electron2_pt`, etc. and pad empty entries with dummy values).
    - `"selection_options"` : specify the values for cuts in your looper (e.g. jet `pt` cut).
   Finally, you can run the looper with:

```
/bin/nice -n 19 python loop.py --nCores 16 --selections "ttH_LeptonicPresel" --debug 1 --options "data/ttH_Leptonic.json" --samples "data/samples_and_scale1fb_ttH.json" --output_tag "test"
```

   Prepending the `loop.py` call with `/bin/nice -n 19` allows us to run on a large number of cores locally without hogging resources and negatively affecting other users.
   The other relevant arguments are:
    - `selections` : specify the string you put into `Preselection/helpers/loop_helper.py` that links to your analysis preselection.
    - `debug` : specifies how much debug info you want printed out (higher = more)
    - `options` : the options `json` you constructed
    - `samples` : the scale1fb `json` you constructed in step 2
    - `output_tag` : a string to identify the output dataframe file and the summary `json` which is also output by `loop.py`
 
5) Plots and tables
   TODO

## Training a BDT
TODO

## Optimizing signal regions to maximize the expected significance
TODO 
