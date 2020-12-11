#!/bin/bash

ENV=./env.sh
source $ENV

if [ "$1" == "-h" ] || [ "$1" == "" ]; then
  echo "Run test."
  echo "Usage: ./runtest.sh {testname}"
  echo ""
  echo "Available tests in $TEST_DATA_ROOT:"
  ls $TEST_DATA_ROOT
  exit
fi

TEST_PATH=$TEST_DATA_ROOT/$1
TMP_PATH=$TEST_DATA_ROOT/$TMP_TEST_NAME

if [ -d $TMP_PATH ]; then
  rm -rf $TMP_PATH
fi
COMMAND=`cat $TEST_PATH/command.sh`

./generate.sh $TMP_TEST_NAME $COMMAND

# Compare all files
diff -r $TEST_PATH $TMP_PATH
