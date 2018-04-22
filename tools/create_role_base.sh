#! /bin/bash
ROLEDIR="`dirname $0`/../roles"

function usage {
    echo "usage: ${0} <name>"
    exit 1
}

if [ -z $1 ]; then
    usage
fi

if [ -d "${ROLEDIR}/${1}" ]; then
    echo "role directory ${1} already exists"
    exit 2
fi

mkdir "${ROLEDIR}/${1}" "${ROLEDIR}/${1}/tasks" "${ROLEDIR}/${1}/defaults"
echo "---" > "${ROLEDIR}/${1}/tasks/main.yml"
echo "---" > "${ROLEDIR}/${1}/defaults/main.yml"
touch "${ROLEDIR}/${1}/README.md"

git add "${ROLEDIR}/${1}"
