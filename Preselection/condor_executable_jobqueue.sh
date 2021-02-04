#!/usr/bin/env bash

if [ -r "$OSGVO_CMSSW_Path"/cmsset_default.sh ]; then source "$OSGVO_CMSSW_Path"/cmsset_default.sh
elif [ -r "$OSG_APP"/cmssoft/cms/cmsset_default.sh ]; then source "$OSG_APP"/cmssoft/cms/cmsset_default.sh
elif [ -r /cvmfs/cms.cern.ch/cmsset_default.sh ]; then source /cvmfs/cms.cern.ch/cmsset_default.sh
else
    echo "ERROR! Couldn't find $OSGVO_CMSSW_Path/cmsset_default.sh or /cvmfs/cms.cern.ch/cmsset_default.sh or $OSG_APP/cmssoft/cms/cmsset_default.sh"
    exit 1
fi

hostname

if ! ls /hadoop/cms/store/ ; then
    echo "ERROR! hadoop is not visible, so the worker would be useless later. dying."
    exit 1
fi

mkdir temp ; cd temp

mv ../{analysisenv.tar.*,*.py} .
#mv ../{daskworkerenv2.tar.*,*.py} .
echo "started extracting at $(date +%s)"
tar xf analysisenv.tar.*
#tar xf daskworkerenv2.tar.* 
echo "finished extracting at $(date +%s)"

source analysisenv/bin/activate
#source daskworkerenv2/bin/activate

ls -lrth
export PYTHONPATH=`pwd`:$PYTHONPATH
export PATH=`pwd`/analysisenv/bin:$PATH
#export PATH=`pwd`/daskworkerenv2/bin:$PATH

$@
