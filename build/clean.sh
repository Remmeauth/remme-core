#!/bin/bash

# Without -a it cleans only REMME images. With -a it cleans also Sawtooth images.

SEARCH_REMME_IMAGES_REGEX='remme\/(?!sawtooth-bare)[a-z-]+(?=\s+latest)'

while getopts ":a" opt; do
    case $opt in
        r)
            SEARCH_REMME_IMAGES='remme\/[a-z-]+(?=\s+latest)'
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit
            ;;
      esac
done

IMAGES=$(docker images | grep -Po  $SEARCH_REMME_IMAGES_REGEX)
for IMAGE in $IMAGES; do
    docker rmi $IMAGE:latest
done

if [ -d "./docs/html" ]; then
    rm -rf ./docs/html
fi
