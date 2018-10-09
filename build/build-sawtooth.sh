#!/bin/bash

BUILD_CMD="docker-compose -f docker-compose-installed.yaml build"

git clone https://github.com/Remmeauth/sawtooth-core.git
cd sawtooth-core
git checkout tags/v1.2.0

$BUILD_CMD settings-tp
$BUILD_CMD validator
$BUILD_CMD rest-api
$BUILD_CMD block-info-tp
$BUILD_CMD devmode-rust

cd ..

docker tag sawtooth-devmode-rust:latest remme/sawtooth-devmode-rust:latest
docker tag sawtooth-rest-api:latest remme/sawtooth-rest-api:latest
docker tag sawtooth-settings-tp:latest remme/sawtooth-settings-tp:latest
