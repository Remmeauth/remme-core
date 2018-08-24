#!/usr/bin/env bash

source ./bash/network-config.env
docker-compose -f docker-compose/base.yml --project-name remme up
