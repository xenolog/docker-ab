#!/bin/sh

if [ -n "${DEBUG}" ] ; then
    set -x
    set -v
fi

if [ -z "${test_parameters__server_port}" ] ; then
    PORT=""
else
    PORT=":${test_parameters__server_port}"
fi

if [ -z "${test_parameters__server_proto}" ] ; then
    PROTO="http"
else
    PROTO="${test_parameters__server_proto}"
fi

if [ "${test_parameters__document_path}" == "/" ] || [ -z "${test_parameters__document_path}" ] ; then
    URI="/" ;
else
    URI="${test_parameters__document_path}" ;
fi

ab -c ${test_parameters__concurrency_level} \
   -n ${test_parameters__requests_number} \
   ${PROTO}://${test_parameters__server_hostname}${PORT}${URI} \
   > ${TEST_CASE_RESULT} ; rc=$?

exit $rc

test_parameters__document_path="/"

