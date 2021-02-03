#!/bin/bash

#####
echo "POSTPRC SUBMISSION"

PACKAGE=package.tar.gz
OUTPUTDIR=$1
OUTPUTFILENAME=$2
INPUTFILENAMES=$3
INDEX=$4
CMSSW_VER=$5

ARGS=$7

echo "[wrapper] OUTPUTDIR	= " ${OUTPUTDIR}
echo "[wrapper] OUTPUTFILENAME	= " ${OUTPUTFILENAME}
echo "[wrapper] INPUTFILENAMES	= " ${INPUTFILENAMES}
echo "[wrapper] INDEX		= " ${INDEX}

echo ${ARGS}
echo ${CMSSW_VER}

echo "[wrapper] printing env"
#printenv
echo 

echo "[wrapper] hostname  = " `hostname`
echo "[wrapper] date      = " `date`
echo "[wrapper] linux timestamp = " `date +%s`

######################
# Set up environment #
######################

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

if [ -r "$OSGVO_CMSSW_Path"/cmsset_default.sh ]; then
    echo "sourcing environment: source $OSGVO_CMSSW_Path/cmsset_default.sh"
    source "$OSGVO_CMSSW_Path"/cmsset_default.sh
elif [ -r "$OSG_APP"/cmssoft/cms/cmsset_default.sh ]; then
    echo "sourcing environment: source $OSG_APP/cmssoft/cms/cmsset_default.sh"
    source "$OSG_APP"/cmssoft/cms/cmsset_default.sh
elif [ -r /cvmfs/cms.cern.ch/cmsset_default.sh ]; then
    echo "sourcing environment: source /cvmfs/cms.cern.ch/cmsset_default.sh"
    source /cvmfs/cms.cern.ch/cmsset_default.sh
else
    echo "ERROR! Couldn't find $OSGVO_CMSSW_Path/cmsset_default.sh or /cvmfs/cms.cern.ch/cmsset_default.sh or $OSG_APP/cmssoft/cms/cmsset_default.sh"
    exit 1
fi

# export SCRAM_ARCH=slc7_amd64_gcc700

echo $PACKAGE 
ls -ltrah *

tar -xf  $PACKAGE
rm package.tar.gz

ls -ltrah *

# Build
cd $CMSSW_VER/src
echo "[wrapper] in directory: " ${PWD}

echo "[wrapper] attempting to build"


scramv1 b ProjectRename
eval `scramv1 runtime -sh`

scram b clean
scram b -j1

echo $CMSSW_BASE
echo "PYTHONPATH"
echo $PYTHONPATH
echo "PATH"
echo $PATH


echo "[wrapper] in directory: " ${PWD}
cd PhysicsTools/NanoAODTools/crab/
echo "[wrapper] in directory: " ${PWD}

echo "python crab_script_local_sysargvfiles.py" ${INPUTFILENAMES} ${ARGS}

echo  ${ARGS}
echo  ${ARGS}
echo  ${ARGS}

python crab_script_local_sysargvfiles.py ${INPUTFILENAMES} ${ARGS}



# Create tag file
#cmsRun Taggers/test/ttH_TagAndDump.py ${INPUTFILENAMES} ${ARGS}

if [ "$?" != "0" ]; then
    echo "Removing output file because cmsRun crashed with exit code $?"
    rm *.root
fi

echo "[wrapper] output root files are currently: "
ls -lh *.root

haddnano.py ${OUTPUTFILENAME}.root *.root

# Copy output
eval `scram unsetenv -sh` # have to add this because CMSSW and gfal interfere with each other or something...

COPY_SRC="file://`pwd`/${OUTPUTFILENAME}.root"
COPY_DEST="gsiftp://gftp.t2.ucsd.edu${OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root"
echo "Running: env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 4200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}"
env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 4200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}

#gfal-copy -p -f -t 4200 --verbose file://`pwd`/${OUTPUTFILENAME}.root gsiftp://gftp.t2.ucsd.edu/${OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root --checksum ADLER32
