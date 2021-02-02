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
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools

# add SVFit packages (using latest version under CMSSW, reference here https://github.com/SVfit/ClassicSVfit/tree/fastMTT_19_02_2019)
git clone https://github.com/SVfit/ClassicSVfit TauAnalysis/ClassicSVfit -b fastMTT_19_02_2019
git clone https://github.com/SVfit/SVfitTF TauAnalysis/SVfitTF

scram b
```

<h2>Submission</h2>

1.local tests

2.submission via crab

3.submission via [ProjectMetis](https://github.com/aminnj/ProjectMetis) 


