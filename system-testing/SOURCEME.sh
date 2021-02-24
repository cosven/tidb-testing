#!/usr/bin/env bash

if [ -z "$ST_NAMESPACE" ]; then
    echo "Please export environment variable ST_NAMESPACE"
    false
else
    ns="$ST_NAMESPACE"

    unalias k
    unalias tkn
    unalias naglfar
    alias k="kubectl -n $ns"
    alias tkn="tkn -n $ns"
    alias naglfar="naglfar -n $ns"

    echo "You now have these aliases with -n option:"
    echo -e "\t\e[36mk=kubectl,tkn=tkn,naglfar=naglfar\e[0m"
    echo -e "You can also try \e[34msource hack/bash_prompt.sh\e[0m"
fi
