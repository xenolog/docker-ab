#!/bin/sh

if [ -n "${DEBUG}" ] ; then
    set -x
    set -v
fi

if [ -z "${test_parameters__port}" ] ; then
    PORT=""
else
    PORT=":${test_parameters__port}"
fi

if [ -z "${test_parameters__proto}" ] ; then
    PROTO="http"
else
    PROTO="${test_parameters__proto}"
fi


ab -c ${test_parameters__concurrency} \
   -n ${test_parameters__requests} \
   ${PROTO}://${test_parameters__host}${PORT}/ > ${TEST_CASE_RESULT} ; rc=$?

exit $rc