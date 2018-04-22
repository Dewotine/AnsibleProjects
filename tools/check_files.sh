#!/usr/bin/env bash

ROLEDIR="`dirname $0`/../roles"
PLAYBOOKDIR="`dirname $0`/../playbooks"
ROLES=$(find ${ROLEDIR} -maxdepth 1 -mindepth 1 -type d | sort)
RC=0
CURRENT_ROLE=""
LOG_TAG=""

source "$(dirname $0)/lib.sh"

# Fatal flag for CI
FATAL_FOUND=0

for R in ${ROLES}; do
    CURRENT_ROLE=$(echo ${R} | awk -F'/' '{print $NF}')
    LOG_TAG="Role: ${CURRENT_ROLE}"
    if [ ! -f "${R}/README.md" ]; then
        log_fatal "Missing README.md"
        RC=1
        FATAL_FOUND=1
        continue
    fi

    # Check if header line is '# Role: <rolename>'
    DOCHEADER="$(head -1 ${R}/README.md)"
    if [ "${DOCHEADER}" != "# Role: ${CURRENT_ROLE}" ]; then
        log "Invalid documentation header line '${DOCHEADER}'"
        RC=1
    fi

    # Check for missing sections
    for SN in "Parameters" "Examples"; do
        SECTION_COUNT=$(grep -c "^## ${SN}" ${R}/README.md)
        if [ ${SECTION_COUNT} -eq 0 ]; then
            log "Missing section '## ${SN}'"
            RC=1
        elif [ ${SECTION_COUNT} -ne 1 ]; then
            log "Multiple sections '## ${SN}'"
            RC=1
        fi
    done

    # Check example marker
    if [ $(grep -c '```' ${R}/README.md) -eq 0 ]; then
        log "Missing examples"
        RC=1
    fi

    # Verify if parameters are present, if there are parameters
    if [ $(grep -c "This role doesn't use any parameter." ${R}/README.md) -eq 0 ]; then
        for PHL in "| Variable | Type | Description | Default |" "| --- | --- | --- | --- |"; do
            PHL_COUNT=$(grep -c "${PHL}" ${R}/README.md)
            if [ ${PHL_COUNT} -eq 0 ]; then
                log_fatal "Missing parameter header '${PHL}' or documentation is not up-to-date."
                FATAL_FOUND=1
                RC=1
            fi
        done
    fi

    # TODO: check if all variables are documented
done

for F in $(find ./roles ./playbooks -type f -name "*.yml" | sort); do
    LOG_TAG="File: ${F}"
    if [ "$(head -1 ${F})" != "---" ]; then
        log_fatal "YAML file doesn't start with '---' header"
        FATAL_FOUND=1
        RC=2
    fi

    if [ $(grep -c $'\r'\$ "${F}") -ne 0 ]; then
        log_fatal 'YAML file has \\r characters'
        FATAL_FOUND=1
        RC=2
    fi
done

for F in $(find roles/*/{tasks,handlers} -name "*.yml" | sort); do
    OLD_TASK_CALL=$(grep -HnE "\s.*[^=][=]{1}[^=]" ${F} |grep -v "\swhen[:]"|grep -v "\swith_.*[:]"|grep -v ".+[:].+[:]#" | wc -l)
    if [ ${OLD_TASK_CALL} -gt 0 ]; then
        LOG_TAG="File: ${F}"
        log "Old task inline format found. This is deprecated."
    fi
done

for F in $(find roles/*/{tasks,handlers} -name "*.yml" | sort); do
    OLD_INCLUDE_CALL=$(grep -Hn "include[:].*" ${F} | wc -l)
    if [ ${OLD_INCLUDE_CALL} -gt 0 ]; then
        LOG_TAG="File: ${F}"
        log "Old include found. This is deprecated. Please replace it with include_tasks or import_tasks."
    fi
done

for F in $(find playbooks -name "*.yml" | sort); do
    OLD_INCLUDE_CALL=$(grep -Hn "include[:].*" ${F} | wc -l)
    if [ ${OLD_INCLUDE_CALL} -gt 0 ]; then
        LOG_TAG="File: ${F}"
        log "Old include found. This is deprecated. Please replace it with import_playbook."
    fi
done

if [ ${FATAL_FOUND} -gt 0 ]; then
	exit ${RC}
fi
