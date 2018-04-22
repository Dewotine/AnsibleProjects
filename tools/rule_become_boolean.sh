#! /usr/bin/env bash

source "$(dirname $0)/lib.sh"

LOG_TAG="become-boolean-rule"
BECOMEBOOL=$(grep -P -R '\sbecome[:] (?!true|false)' playbooks roles)
if [ "${BECOMEBOOL}" != "" ]; then
    log_fatal "Some become rules are not satisfied. Become values must be [true, false]"
    grep -P -R '\sbecome[:] (?!true|false)' playbooks roles
    exit 1
fi