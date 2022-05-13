#!/usr/bin/env bash

ROOT=$(unset CDPATH && cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd $ROOT

source hack/lib.sh

function st::setup_aliases() {
    local ns="$1"
    unalias k 2>%1
    unalias tkn 2>%1
    unalias naglfar 2>%1
    unalias tkn-start-task 2>%1
    unalias tkn-start-pipeline 2>%1

    alias tkn="tkn -n $ST_NAMESPACE"
    alias tkn-start-task="tkn -n $ST_NAMESPACE task start -s $ST_TEKTON_SA -w name=manifest,emptyDir="""
    alias tkn-start-pipeline="tkn -n $ST_NAMESPACE pipeline start -s $ST_TEKTON_SA -w name=manifest,emptyDir="""
    echo -e "Tekton tasks/pipelines all run in namespace \e[36m$ST_NAMESPACE\e[0m"

    alias k="kubectl -n $ns"
    alias naglfar="naglfar -n $ns"
    echo "You now have these aliases with -n option:"
    echo -e "\t\e[36mk=kubectl,naglfar=naglfar\e[0m"
}

# Command
function st-use-ns() {
    if [ -z "$1" ]; then
        echo "Usage: st-use-ns NAMESPACE"
        false
    else
        export ST_NAMESPACE="$1"
        echo -e "System testing resources namespace is \e[36m$1\e[0m"
        st::setup_aliases "$ST_NAMESPACE"
        if [ $? -eq 0 ]; then
           echo -e "You can also try \e[34msource hack/bash_prompt.sh\e[0m"
        fi
    fi
}

ST_TEKTON_SA="system-testing"

st-use-ns "$ST_NAMESPACE"
