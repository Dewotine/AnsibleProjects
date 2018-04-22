#! /usr/bin/env bash

function log() {
    echo -e "\033[0;33m[${LOG_TAG}]\033[0m -- ${1}"
}

function log_fatal() {
    echo -e "\033[1;31m[${LOG_TAG}]\033[0m -- \033[0;31m${1}\033[0m"
}