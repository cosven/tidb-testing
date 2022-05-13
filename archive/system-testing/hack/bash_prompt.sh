#!/usr/bin/env bash

# This script show the system testing namespace in the prompt PS1
#
# Usage: source hack/bash_prompt.sh

function __get_st_ns {
    if [ -z "$ST_PROMPT_COMMAND" ]; then
        echo ""
    else
        if [ -z "$ST_NAMESPACE" ]; then
            echo ""
        else
            echo "($ST_NAMESPACE) "
        fi
    fi
}

function __st_prompt_command {
    PS1="`__get_st_ns`${PS1}"
}

function st-prompt-activate {
    export ST_PROMPT_COMMAND="on"
    echo "Run 'st-prompt-deactivate' to deactivate."
}


function st-prompt-deactivate {
    unset ST_PROMPT_COMMAND
}


st-prompt-activate

if [[ $PROMPT_COMMAND != *"__st_prompt_command"* ]]; then
    export PROMPT_COMMAND="$PROMPT_COMMAND;__st_prompt_command"
fi
