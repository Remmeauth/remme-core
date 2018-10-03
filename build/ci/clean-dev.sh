#!/bin/bash

./build/clean.sh

IMAGES=$(docker images | grep -Po 'remmetechnical\/[a-z-]+(?=\s+latest)')
for IMAGE in $IMAGES; do
    docker rmi $IMAGE:latest
done
