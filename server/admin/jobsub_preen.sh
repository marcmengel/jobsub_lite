#!/bin/sh
HERE=`dirname $0`
source $HERE/config_lib.sh
get_jobsub_env


/opt/jobsub/server/admin/jobsub_preen.py $@


