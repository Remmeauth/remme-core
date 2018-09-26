#!/usr/bin/env bash

source ./config/network-config.env
docker-compose -f docker-compose/base.yml --project-name remme up
