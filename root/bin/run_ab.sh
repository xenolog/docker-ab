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

sc-runner --config="${SETTINGS_YAML}" --config="${INPUT_YAML_FILE}" --outputs-dir="${OUTPUT_DIR}" --result-dir="${OUTPUT_DIR}" ; rc=$?

echo "done."
exit $rc