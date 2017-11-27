#!/bin/sh

. /test_globals.env

: "${test_run_id:=00000000}"

echo "JOB: $test_run_id"
echo "AB: $*"

TEST_RESULT_DIR="${STORAGE_DIR}/$(date +%Y%m%d-%H%M%S-%Z)__${test_run_id}"
echo "Results stored: ${TEST_RESULT_DIR}"

SETTINGS_FILE_NAME="${TEST_RESULT_DIR}/settings.env"
RESULT_FILE_NAME="${TEST_RESULT_DIR}/ab.txt"
RC_FILE_NAME="${TEST_RESULT_DIR}/rc.txt"

mkdir -p "${STORAGE_DIR}"
mkdir -p "${TEST_RESULT_DIR}"

export | grep -e 'export test_' -e 'export vnf_' -e 'export pass_criteria' | sed -re 's/export //' > $SETTINGS_FILE_NAME
ab $* 2>&1 > $RESULT_FILE_NAME
rc=$?
echo $rc > $RC_FILE_NAME

###