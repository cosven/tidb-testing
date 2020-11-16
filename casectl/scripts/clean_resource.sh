#!/bin/bash

shopt -s expand_aliases
source .env

if [[ -z "$1" ]]; then
    echo "Usage: $1 <case-fullname>"
    exit 1
fi

ns="$1"
instance="$1"

k -n $ns delete tc $instance
k -n $ns delete pvc -l app.kubernetes.io/instance=$instance
