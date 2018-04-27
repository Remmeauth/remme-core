#!/usr/bin/env bash

source .env
docker-compose -f docker-compose/dev.yml -f docker-compose/run.yml up
