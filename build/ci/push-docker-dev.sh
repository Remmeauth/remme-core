#!/bin/bash

IMAGES=$(docker images | grep -Po '(?<=remmetechnical\/)[a-z-]+(?=\s+latest)')
RELEASE_NUMBER=$(git describe --abbrev=0 --tags)

for IMAGE in $IMAGES; do
    docker push remmetechnical/$IMAGE:latest
done
