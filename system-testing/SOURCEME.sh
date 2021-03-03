#!/usr/bin/env bash

ROOT=$(unset CDPATH && cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd $ROOT

source hack/lib.sh

function st::setup_aliases() {
    local ns="$1"
    unalias k
    unalias tkn
    unalias naglfar
    alias k="kubectl -n $ns"
    alias tkn="tkn -n $ns"
    alias naglfar="naglfar -n $ns"
    echo "You now have these aliases with -n option:"
    echo -e "\t\e[36mk=kubectl,tkn=tkn,naglfar=naglfar\e[0m"
}

# Command
function st-use-ns() {
    if [ -z "$1" ]; then
        echo "Usage: st-use-ns NAMESPACE"
        false
    else
        export ST_NAMESPACE="$1"
        echo "System testing namespace is $1"
        st::setup_aliases "$ST_NAMESPACE"
        if [ $? -eq 0 ]; then
           echo -e "You can also try \e[34msource hack/bash_prompt.sh\e[0m"
        fi
    fi
}


st-use-ns "$ST_NAMESPACE"
