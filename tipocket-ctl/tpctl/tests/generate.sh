#!/bin/bash

ENV=./env.sh
source $ENV

if [ "$1" == "-h" ] || [ "$1" == "" ]; then
  echo "Generate test based on right command"
  echo "Usage: ./generate.sh {test_name} {test_command}"
  echo "  test data would be stored in $TEST_ROOT/data/{test_name}"
  exit
fi

TEST_NAME=$1
TEST_COMMAND=${@:2}

TEST_DIR=$TEST_DATA_ROOT/$TEST_NAME

if [ -d $TEST_DIR ]
then
  echo "Directory $TEST_DIR exists, exit."
  exit 1
fi

mkdir -p $TEST_DIR
echo $TEST_COMMAND >> $TEST_DIR/command.sh

cd $TIPOCKET_PATH

if [ -d tpctl-build/ ]; then
  rm -r tpctl-build/
fi

$TEST_COMMAND > $TEST_DIR/cli-output.txt
cp -r tpctl-build/ $TEST_DIR/tpctl-build
rm -rf tpctl-build/
cd $TEST_ROOT
