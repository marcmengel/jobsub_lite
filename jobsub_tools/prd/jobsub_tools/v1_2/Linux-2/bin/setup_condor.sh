#!/bin/sh

if [ "$SUBMIT_HOST" = "" ]
then
	export SUBMIT_HOST=gpsn01.fnal.gov
fi

if [ "$GROUP" = "" ]
then
	export GROUP=`id -gn`
fi
export PATH=${PATH}:${JOBSUB_TOOLS_DIR}/bin/condor_wrappers
export source_me=`${JOBSUB_TOOLS_DIR}/bin/setup_condor_sh.py`
unset JOBSUB_UNSUPPORTED_EXPERIMENT

source $source_me
#/bin/rm $source_me
unset source_me


PARENT_DIR=`dirname $CONDOR_TMP`  > /dev/null 2>&1
if [ ! -e $PARENT_DIR ]
then
    mkdir -p $PARENT_DIR
    chgrp ${STORAGE_GROUP} $PARENT_DIR
    chmod g+w $PARENT_DIR
fi

if [ ! -e $CONDOR_TMP ]
then
    mkdir -p $CONDOR_TMP
    chgrp ${STORAGE_GROUP} $CONDOR_TMP 
    chmod g+w $CONDOR_TMP
fi
	
PARENT_DIR=`dirname $CONDOR_EXEC`  > /dev/null 2>&1
if [ ! -e $PARENT_DIR ]
then
    mkdir -p $PARENT_DIR
    chgrp ${STORAGE_GROUP} $PARENT_DIR
    chmod g+w $PARENT_DIR
fi
if [ ! -e $CONDOR_EXEC ]
then
    mkdir -p $CONDOR_EXEC
    chgrp ${STORAGE_GROUP} $CONDOR_EXEC
    chmod g+w $CONDOR_EXEC
fi
if [ "$JOBSUB_UNSUPPORTED_EXPERIMENT" == "TRUE" ]
then
	if [ "$GROUP" == "" ] 
	then
		echo "warning: no \$GROUP variable set"
	else
		echo "warning: GROUP variable set to '$GROUP', dont know what to do"
	fi
	echo "warning: your GROUP env variable and your gid="`id -gn`
	echo "did not identify you as belonging to a supported experiment, setting  GROUP = "$GROUP
	echo "you may submit to the local batch system but your OSG grid"
	echo "access probably will not work unless you have set up a cron job to keep your \\fermilab proxy alive"
	echo "see " 
	echo "https://cdcvs.fnal.gov/redmine/projects/ifront/wiki/Getting_Started_on_GPCF#Set-up-Grid-permissions-and-proxies-before-you-submit-a-job"
	echo "and"
        echo "https://cdcvs.fnal.gov/redmine/projects/ifront/wiki/UsingJobSub#The-probably-will-not-work-error-how-to-make-it-work" 
fi
