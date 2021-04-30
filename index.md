## Introduction 

`HggAnalysisDev` is a repository of tools for fast and flexible development of H->gg analyses.
The main components are:
1. **Preselection**: loop over nanoAODs and write events to a `pandas` dataframe, make plots and tables from these dataframes
2. **MVA Training & Evaluation**: starting from output of 1 (`pandas` dataframe), train and evaluate BDTs (using `xgboost`) and deep neural networks (using `tensorflow` and `keras`), plot performance metrics, and zip MVA scores back into dataframes.
3. **Signal Region Optimization**: scan a variety of cuts on one or more variables (typically MVAs) to define signal regions. Within each signal region, fit `m_gg` distribution to create signal and background (non-resonant and resonant) models, and evaluate a figure of merit (significance, upper limit, etc) in these signal regions.

**Note**: step 3 currently relies on old code from the ttH (HIG-19-013/HIG-19-015) and FCNC (TOP-20-007) analyses which has `CMSSW` and `combine` dependencies. Planned to be updated to a pure-python implementation using `zfit` and `hepstats`.

## Tutorial
This provides a walkthrough for developing a new H->gg analysis from end-to-end. It assumes you already have custom nanoAOD files with the diphoton preselection applied (see Hgg common tools AN-2019/149) and relevant photon branches for performing the diphoton preselection (these are not present in default nanoAOD at the time of writing).

As an example, we will develop an analysis for measuring ttH (H->gg) in the leptonic (semi-leptonic and di-leptonic decays of ttbar) channel.

1. Identify relevant samples
```
code
```
