#!/usr/bin/env bash

if [ -z "$ST_NAMESPACE" ]; then
    echo "Please export environment variable ST_NAMESPACE"
    false
else
    ns="$ST_NAMESPACE"

    unalias k
    unalias tkn
    alias k="kubectl -n $ns"
    alias tkn="tkn -n $ns"

    echo "You now have two aliases: k=kubectl,tkn=tkn"
    echo -e "You can also try \e[34msource hack/bash_prompt.sh\e[0m"
fi
