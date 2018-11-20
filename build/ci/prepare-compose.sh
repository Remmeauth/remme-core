#!/bin/bash

REMMETECHNICAL_REGEX='s/remme\/([a-z-]+):latest/remmetechnical\/\1:latest/g'

sed -i -E -e $REMMETECHNICAL_REGEX ./build/docker-compose.yml
sed -i -E -e $REMMETECHNICAL_REGEX ./docker/compose/*.yml
