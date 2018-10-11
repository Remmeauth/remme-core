#!/bin/bash

git submodule update --init
docker-compose -f ./build/docker-compose.yml build