#!/bin/sh

if [ -n "${DEBUG}" ] ; then
    set -x
    set -v
fi

: "${INPUT_DIR:=/var/lib/agent_input}"
: "${OUTPUT_DIR:=/var/lib/agent_output}"
: "${INPUT_JSON:=task_properties.json}"
: "${OUTPUT_JSON:=task_result.json}"
: "${TMP_DIR:=/tmp}"

export INPUT_DIR
export INPUT_JSON
export OUTPUT_DIR
export OUTPUT_JSON
export TMP_DIR

INPUT_JSON_FILE="${INPUT_DIR}/${INPUT_JSON}"
OUTPUT_JSON_FILE="${OUTPUT_DIR}/${OUTPUT_JSON}"

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

TASK_SETTINGS="${TMP_DIR}/task_settings.env"
json2env --export ${INPUT_JSON_FILE} > "${TASK_SETTINGS}"
. ${TASK_SETTINGS}

export TEST_CASE_RESULT="${TMP_DIR}/test_case_result.txt"
/usr/lib/test_cases/test_case__${test_scenario_id}.sh ; rc=$?

if [ "$rc" != "0" ] ; then
    # TODO: #16252 more powerfull logic for pass/fail test evaluate
    echo "--------" >&2
    echo "Warning! non-zero RC-code. (rc=${rc})" >&2
    echo "--------" >&2
    export test_result="failed"
    gen_json_adder --incoming="${INPUT_JSON_FILE}" > "${OUTPUT_JSON_FILE}"
    rc=1
else
    export test_result="passed"
    export TEST_CASE_RESULT_JSON="${TMP_DIR}/test_case_result.json"
    cat "${TEST_CASE_RESULT}" | ab2json --generic > "${TEST_CASE_RESULT_JSON}"
    gen_json_adder --incoming="${INPUT_JSON_FILE}" \
                   --result="${TEST_CASE_RESULT_JSON}" > "${OUTPUT_JSON_FILE}"
    rc=0
fi

echo "done."
exit $rc