#!/bin/bash

docker pull remmetechnical/sawtooth-validator-intermediate:latest
docker tag remmetechnical/sawtooth-validator-intermediate:latest sawtooth-validator:latest

COMPOSE_FILES="-f ./build/docker-compose.yml"

while getopts ":r" opt; do
    case $opt in
        r)
            echo "Running build in the release mode. This build do not use cache so it may take longer."
            COMPOSE_FILES="$COMPOSE_FILES -f ./build/docker-compose-release.yml"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit
            ;;
      esac
done

echo "Updating git submodules..."
git submodule update --init

echo "Running REMME build..."
docker-compose $COMPOSE_FILES build