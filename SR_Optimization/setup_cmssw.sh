export SCRAM_ARCH=slc7_amd64_gcc700
if [ ! -d CMSSW_10_2_13 ]; then
    cmsrel CMSSW_10_2_13
    cd CMSSW_10_2_13/src
    cmsenv
    git cms-init

    # Install the GBRLikelihood package which contains the RooDoubleCBFast implementation
    git clone git@github.com:jonathon-langford/HiggsAnalysis.git

    # Install Combine as per the documentation here: cms-analysis.github.io/HiggsAnalysis-CombinedLimit/
    git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

    # compile
    scram b -j 20
    cd ../..
fi

pushd CMSSW_10_2_13/src
cmsenv
popd
