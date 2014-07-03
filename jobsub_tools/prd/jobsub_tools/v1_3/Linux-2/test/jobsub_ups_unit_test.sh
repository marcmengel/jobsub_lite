#!/bin/bash

source $UPS_DIR/test/unittest.bash

test_setup() {
   testdir=/tmp/t$$
   mkdir -p $testdir/tmp
   mkdir -p $testdir/exec
   export CONDOR_TMP=$testdir/tmp
   export CONDOR_EXEC=$testdir/exec
}

test_teardown() {
   return 0
   rm -rf $testdir
}

print_cmd_file() {
   echo command file: $file
   return 0
   # print file, so error report is helpful if it fails
   echo "cmd file:"
   echo "----"
   cat $file
   echo
   echo "----"
}

test_lines() {
   file=`jobsub -n  -lines="foo" -lines="bar" /usr/bin/printenv`

   print_cmd_file

   # succeeds if foo and bar are in the file
   grep foo $file /dev/null && grep bar $file /dev/null
}


test_append_requirements1() {
   SUBMIT_HOST=gpsn01.fnal.gov
   file=`jobsub -n -e SUBMIT_HOST  --append_condor_requirements=foo -c bar /usr/bin/printenv`

   print_cmd_file
   # succeeds if foo and bar are in the file, and in the requirements line
   grep 'requirements.*foo' $file /dev/null && grep 'requirements.*bar' $file /dev/null
}

test_append_requirements2() {
   SUBMIT_HOST=gpsn01.fnal.gov
   file=`jobsub -n -e SUBMIT_HOST  -g --append_condor_requirements=foo -c bar /usr/bin/printenv`

   print_cmd_file
   # succeeds if foo and bar are in the file, and in the requirements line
   grep 'requirements.*foo' $file /dev/null && grep 'requirements.*bar' $file /dev/null
}


test_append_requirements3() {
   SUBMIT_HOST=not.gpsn01.fnal.gov
   file=`jobsub -e SUBMIT_HOST -n  --append_condor_requirements=foo -c bar /usr/bin/printenv`

   print_cmd_file
   # succeeds if foo and bar are in the file, and in the requirements line
   grep 'requirements.*foo' $file /dev/null && grep 'requirements.*bar' $file /dev/null
}

test_append_requirements4() {
   SUBMIT_HOST=not.gpsn01.fnal.gov
   file=`jobsub -e SUBMIT_HOST -n -g  --append_condor_requirements=foo -c bar /usr/bin/printenv`

   print_cmd_file
   # succeeds if foo and bar are in the file, and in the requirements line
   grep 'requirements.*foo' $file /dev/null && grep 'requirements.*bar' $file /dev/null
}

test_append_accounting_group() {
   SUBMIT_HOST=gpsn01.fnal.gov
   file=`jobsub -n -g -l '+AccountingGroup = "group_highprio.minervapro"' /usr/bin/printenv`
   print_cmd_file

   # succeeds if +AccountingGroup = "group_highprio.minervapro" appears last of all +AccountingGroup s
   grep 'AccountingGroup' $file > ${file}.1
   tail -1 ${file}.1 > ${file}.2
   grep 'group_highprio.minervapro' ${file}.2 
}

test_OS() {
   SUBMIT_HOST=gpsn01.fnal.gov
   file=`jobsub -n -g --OS=foo,bar /usr/bin/printenv`
   print_cmd_file

   # succeeds if foo and bar are in the DesiredOS line
   grep 'DesiredOS *= *"foo,bar"' $file /dev/null && grep 'requirements.*DesiredOS' $file /dev/null
}  


testsuite setups_suite	\
    -s test_setup 	\
    -t test_teardown	\
    test_lines		\
    test_append_requirements1 \
    test_append_requirements2 \
    test_append_requirements3 \
    test_append_requirements4 \
    test_append_accounting_group \
    test_OS \
   

setups_suite "$@"
