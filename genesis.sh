#!/usr/bin/env bash

DEFAULT_SUPPLY=10000000000000
TOTAL_SUPPLY=${1:-${DEFAULT_SUPPLY}}

docker-compose -f docker-compose.genesis.yml run -e REM_TOKEN_SUPPLY=${TOTAL_SUPPLY} genesis
