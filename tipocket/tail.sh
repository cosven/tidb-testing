#!/bin/bash

shopt -s expand_aliases
source .env

if [[ -z "$1" ]]; then
    echo "Usage: $0 <case>"
    exit 1
fi

ns="$1"
instance="$1"

function getCasePodName(){
    k get po --sort-by=.status.startTime | grep $instance | tail -1 | awk '{print $1}'
}

k logs `getCasePodName` -c main "${@:2}"
