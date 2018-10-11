#!/bin/bash

git submodule update --init
docker-compose -f ./build/docker-compose.yml -f ./build/docker-compose-release.yml build