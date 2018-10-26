#!/bin/bash

REMMETECHNICAL_REGEX='s/remme\/([a-z-]+):latest/remmetechnical\/\1:latest/g'
COMMAND='sed -i -E -e $REMMETECHNICAL_REGEX'

$COMMAND ./build/*.yml
$COMMAND ./docker/compose/*.yml
