#!/bin/bash

git submodule update --init
docker build -t remme/remme-core:latest -f ./docker/development.dockerfile .
docker-compose -f ./tests/docker-compose.yml up --build --abort-on-container-exit
docker-compose -f ./docker/compose/testing.yml up --abort-on-container-exit