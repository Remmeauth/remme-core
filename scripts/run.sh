#!/bin/bash

GENESIS_MODE=0
OPERATION_SPECIFIED=0
OPERATION=u
BG_MODE=0
MONITORING_MODE=0
PANEL_MODE=0

source ./config/network-config.env

export REMME_REST_API_PORT
export REMME_VALIDATOR_PORT
export REMME_VALIDATOR_IP

eval_with_log() {
    cmd=$1
    echo -e "\033[90m$ $cmd\033[0m\n"
    eval $cmd
}

function check_op {
    if [ $OPERATION_SPECIFIED -eq 1 ]; then
        echo "Cannot specify two operations at once! You have already specified -$OPERATION"
        exit
    fi
    OPERATION_SPECIFIED=1
}

while getopts ":gudblmp" opt; do
    case $opt in
        g)
            GENESIS_MODE=1
            ;;
        u)
            check_op
            OPERATION=u
            ;;
        d)
            check_op
            OPERATION=d
            ;;
        b)
            BG_MODE=1
            ;;
        m)
            MONITORING_MODE=1
            ;;
        p)
            PANEL_MODE=1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit
            ;;
      esac
done

COMPOSE_DIR=./docker/compose

COMPOSE_FILES="-f $COMPOSE_DIR/base.yml"
if [ $GENESIS_MODE -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/genesis.yml"
    if [ ${DEV:-0} -eq 1 ]; then
        COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/development-genesis.yml"
    fi
fi

if [ $MONITORING_MODE -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/mon.yml"
fi

if [ $PANEL_MODE -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/admin.yml"
fi

if [ ${DEV:-0} -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/development.yml"
fi

ADDITIONAL_ARGS=""
if [ $BG_MODE -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/bg.yml"
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS -d"
fi

if [ ${RESTART_ALWAYS:-0} -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/restart-always.yml"
fi

COMMAND="docker-compose $COMPOSE_FILES --project-name remme"

if [ "$OPERATION" == "u" ]; then
    eval_with_log "$COMMAND up $ADDITIONAL_ARGS"
else
    eval_with_log "$COMMAND down"
fi
