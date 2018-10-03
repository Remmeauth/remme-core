#!/bin/bash

IMAGES=$(docker images | grep -Po '(?<=remme\/)[a-z-]+(?=\s+latest)')
RELEASE_NUMBER=$(git describe --abbrev=0 --tags)

for IMAGE in $IMAGES; do
    docker push remme/$IMAGE:latest
    docker push remme/$IMAGE:$RELEASE_NUMBER
done