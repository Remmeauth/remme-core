#!/bin/bash

find remme/protos -type f -name '*_pb2.py' -delete
protoc -I=./protos --python_out=./remme/protos ./protos/*.proto

python3 -m remme.rpc_api
