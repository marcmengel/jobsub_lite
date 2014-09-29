#!/bin/sh 

function pass_or_fail {
if [ "$?" == "0" ]; then
    echo "PASSED"
else
    echo "FAILED"
fi
}


SERVER=$1
if [ "$SERVER" = "" ]; then
    echo "usage: $0 servername"
    echo "run integration tests on servername"
    exit 0
fi
if [ "$GROUP" = "" ]; then
    export GROUP=nova
fi
if [ "$GROUP" = "cdf" ]; then
    export SUBMIT_FLAGS=" $SUBMIT_FLAGS --tar_file_name dropbox://junk.tgz -N 2 "
fi
echo test simple submission
RSLT=`sh ${TEST_FLAG} ./test_simple_submit.sh $SERVER simple_worker_script.sh 1`
echo "$RSLT" >$1.submit.$GROUP.log 2>1&
JID=`echo "$RSLT" | grep 'se job id' | awk '{print $4}'`
GOTJID=`echo $JID| grep '[0-9].0@'`
SUBMIT_WORKED=$?
if [ "$SUBMIT_WORKED" = "0" ]; then
     echo "successfully submitted job $GOTJID"
else
    echo "submission problem, please see file $1.submit.$GROUP.log"
fi 

echo test submission with role
RSLT2=`sh ${TEST_FLAG} ./test_simple_submit_with_role.sh $SERVER simple_worker_script.sh 1` 
echo "$RSLT2" >$1.submit_role.$GROUP.log 2>1&
JID2=`echo "$RSLT2" | grep 'se job id' | awk '{print $4}'`
GOTJID2=`echo $JID2| grep '[0-9].0@'`
SUBMIT_WORKED2=$?
if [ "$SUBMIT_WORKED2" = "0" ]; then
     echo "PASSED successfully submitted job $GOTJID2"
else
    echo "FAILED submission problem, please see file $1.submit_role.$GROUP.log"
fi 
echo testing holding and releasing
sh ${TEST_FLAG} ./test_hold_release.sh $SERVER $GOTJID2 >$1.holdrelease.$GROUP.log 2>&1
pass_or_fail
echo testing dropbox functionality
sh ${TEST_FLAG} ./test_dropbox_submit.sh $SERVER simple_worker_script.sh >$1.dropbox.$GROUP.log 2>&1
pass_or_fail
echo test helpfile
sh ${TEST_FLAG} ./test_help.sh $SERVER >$1.help.$GROUP.log 2>&1
pass_or_fail
echo test listing jobs
sh ${TEST_FLAG} ./test_listjobs.sh $SERVER $GOTJID2 >$1.list.$GROUP.log 2>&1
pass_or_fail
echo test condor_history
sh ${TEST_FLAG} ./test_history.sh $SERVER $GOTJID2 >$1.history.$GROUP.log 2>&1
pass_or_fail
echo test retrieving zip_file from sandbox
sh ${TEST_FLAG} ./retrieve_sandbox.sh $SERVER $GOTJID2 >$1.sandbox.$GROUP.log 2>&1
pass_or_fail
echo testing removing job
sh ${TEST_FLAG} ./test_rm.sh  $SERVER $GOTJID2 >$1.testrm.$GROUP.log  2>&1
pass_or_fail
echo testing dag submission 
sh ${TEST_FLAG} ./test_dag_submit.sh  $SERVER  >$1.testdag.$GROUP.log  2>&1
pass_or_fail
echo testing cdf sam job
cd cdf_dag_test
sh ${TEST_FLAG} ./cdf_sam_test.sh $SERVER >../$1.test_cdf_sam_job.log 2>&1
pass_or_fail
cd -
./api_coverage_test.sh MACH=$SERVER GROUP=$GROUP
for bug in `ls bug_tests`; do cd bug_tests/$bug ;   ./${bug}_test.sh $SERVER >${bug}.out 2>&1 ;  ./${bug}_report.sh; cd ../.. ; done
