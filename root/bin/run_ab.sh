#!/bin/sh

if [ -n "${DEBUG}" ] ; then
    set -x
    set -v
fi

: "${INPUT_DIR:=/var/lib/agent_input}"
: "${OUTPUT_DIR:=/var/lib/agent_output}"
: "${SETTINGS_YAML:=/usr/lib/test_cases/settings.yaml}"
: "${INPUT_YAML:=task_properties.yaml}"
: "${TMP_DIR:=/tmp}"

export INPUT_DIR
export SETTINGS_YAML
export INPUT_YAML
export OUTPUT_DIR
export TMP_DIR

INPUT_YAML_FILE="${INPUT_DIR}/${INPUT_YAML}"

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

# TASK_SETTINGS="${TMP_DIR}/task_settings.env"
# json2env --export ${INPUT_YAML_FILE} > "${TASK_SETTINGS}"
# . ${TASK_SETTINGS}

sc-runner --config="${SETTINGS_YAML}" --config="${INPUT_YAML_FILE}" --outputs-dir="${OUTPUT_DIR}" --result-dir="${OUTPUT_DIR}"

# export TEST_CASE_RESULT="${TMP_DIR}/test_case_result.txt"
# /usr/lib/test_cases/test_case__${test_scenario_id}.sh ; rc=$?

# if [ "$rc" != "0" ] ; then
#     # TODO: #16252 more powerfull logic for pass/fail test evaluate
#     echo "--------" >&2
#     echo "Warning! non-zero RC-code. (rc=${rc})" >&2
#     echo "--------" >&2
#     export test_result="failed"
#     gen_json_adder --incoming="${INPUT_YAML_FILE}" > "${OUTPUT_DIR_FILE}"
#     rc=1
# else
#     export test_result="passed"
#     export TEST_CASE_RESULT_JSON="${TMP_DIR}/test_case_result.json"
#     cat "${TEST_CASE_RESULT}" | ab2json --generic > "${TEST_CASE_RESULT_JSON}"
#     gen_json_adder --incoming="${INPUT_YAML_FILE}" \
#                    --result="${TEST_CASE_RESULT_JSON}" > "${OUTPUT_DIR_FILE}"
#     rc=0
# fi

echo "done."
exit $rc