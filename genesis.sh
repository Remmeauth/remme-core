#!/usr/bin/env bash

source .env
docker-compose -f docker-compose/base.yml -f docker-compose/genesis.yml up
