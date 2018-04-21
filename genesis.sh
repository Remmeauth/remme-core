#!/usr/bin/env bash

source .env
docker-compose -f docker-compose/dev.yml -f docker-compose/genesis.yml -f docker-compose/run.yml up
