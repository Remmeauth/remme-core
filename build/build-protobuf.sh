#!/bin/bash

protoc -I=./protos --python_out=./remme/protos ./protos/*.proto
