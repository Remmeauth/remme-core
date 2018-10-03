#!/bin/bash

git submodule update --init
docker build --target build -t remme/remme-core-dev:latest .
docker-compose -f ./tests/docker-compose.yml up --build --abort-on-container-exit