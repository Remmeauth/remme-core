#!/bin/bash

git submodule update --init
docker build --target test -t remme/remme-core-dev:latest .
docker-compose -f ./tests/docker-compose.yml up --build --abort-on-container-exit