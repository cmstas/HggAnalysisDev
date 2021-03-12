<h2>Skimming code</h2>

skimming code for the HH -> gg tautau analysis

the skimming code is based on the most recent version of the centrally maintained [nanoAOD-tools](https://github.com/cms-nanoAOD/nanoAOD-tools)  

custom modules and photon sytematics are currently added to this branch [hhggtautau_skim](https://github.com/leonardogiannini/nanoAOD-tools/tree/hhggtautau_skim)  

in order to use the tools for skimming samples (working under CMSSW):

```console
cmsrel CMSSW_10_2_22
cd CMSSW_10_2_22/src/
cmsenv

# add nanoAOD-tools package
git clone -b hhggtautau_skim https://github.com/leonardogiannini/nanoAOD-tools.git PhysicsTools/NanoAODTools

# add SVFit packages (using latest version under CMSSW, reference here https://github.com/SVfit/ClassicSVfit/tree/fastMTT_19_02_2019)
git clone https://github.com/SVfit/ClassicSVfit TauAnalysis/ClassicSVfit -b fastMTT_19_02_2019
git clone https://github.com/SVfit/SVfitTF TauAnalysis/SVfitTF

scram b
```

<h3>1. local tests</h3>

a local test of the postprocessor modules can be run using https://github.com/leonardogiannini/nanoAOD-tools/blob/hhggtautau_skim/crab/local_test.py

the modules used are 

- puAutoWeight_2018(),jetmetUncertainties2018(),muonScaleRes2018() =>  centrally maintained
- gammaSF(), HggModule2018(), gammaWeightSF() => Hgg specific, need to use the custom nanoaod, to check consistency with flashgg
- HHggtautaulep2018() => categories by leptons decay for HHggtautau
- HHggtautauModule2018LVVV(), HHggtautauModule2018LL(), HHggtautauModule2018MM() => possible selections of HHggtautau, with SVFit mass computation included

<h3>2. submission via crab</h3>

the submission via crab can be handled using the scripts in the crab folder of the skim repo.

- [crab_cfg_ggOnly.py](https://github.com/leonardogiannini/nanoAOD-tools/blob/hhggtautau_skim/crab/crab_cfg_ggOnly.py)
- [crab_cfg_ggtautauFull.py](https://github.com/leonardogiannini/nanoAOD-tools/blob/hhggtautau_skim/crab/crab_cfg_ggtautauFull.py)

the two configuration submit the skim either with the ggOnly preselection and relative modules activated, or with the full tautau variables computation

the configurations make use of the lists of samples generated via the [make_samples.py](https://github.com/cmstas/HggAnalysisDev/blob/main/Skimming/make_samples.py) script.
the script works only locally at UCSD, therefore the outputs [sa.py](https://github.com/cmstas/HggAnalysisDev/blob/main/Skimming/sa.py) and [allsamples.py](https://github.com/cmstas/HggAnalysisDev/blob/main/Skimming/allsamples.py) are also stored in the repo.

the files are expected to be found in the folder HggAnalysisDev/Skimming, where HggAnalysisDev should be in the same path of the $CMSSW_BASE environment. (this can be cahnged at the time of submission in case it's needed.)

Before submitting remember to create a proxy certificate and setup crab (cmsenv && source /cvmfs/cms.cern.ch/common/crab-setup.sh)
IN case of submission errors you can find info here https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3ConfigurationFile or in similar pages.

the crab configurations are set to submit all the jobs for all the datasets. if you want to experiment, please reduce [allsamples.py](https://github.com/cmstas/HggAnalysisDev/blob/main/Skimming/allsamples.py) to a single sample, try the --dry-run option, etc.

<h3>3. submission via ProjectMetis</h3>

first checkout the repository https://github.com/aminnj/ProjectMetis and set up environment via ```source setup.sh```

then use the example you find in this repository.

<h2>Content of the modules</h2>

- gammaSF()
- HggModule2018()
- gammaWeightSF()

etc.

