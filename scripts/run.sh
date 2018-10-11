#!/bin/bash

GENESIS_MODE=0
OPERATION_SPECIFIED=0
OPERATION=u
BG_MODE=0
RUN_LOGIO=0

source ./config/network-config.env

function check_op {
    if [ $OPERATION_SPECIFIED -eq 1 ]; then
        echo "Cannot specify two operations at once! You have already specified -$OPERATION"
        exit
    fi
    OPERATION_SPECIFIED=1
}

while getopts ":gudbl" opt; do
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
        l)
            RUN_LOGIO=1
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
fi
if [ $RUN_LOGIO -eq 1 ]; then
    COMPOSE_FILES="-f $COMPOSE_DIR/logio.yml"
fi

ADDITIONAL_ARGS=""
if [ $BG_MODE -eq 1 ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f $COMPOSE_DIR/bg.yml"
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS -d"
fi

COMMAND="docker-compose $COMPOSE_FILES --project-name remme"

if [ "$OPERATION" == "u" ]; then
    $COMMAND up $ADDITIONAL_ARGS
else
    $COMMAND down
fi