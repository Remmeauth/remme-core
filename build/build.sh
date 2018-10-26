#!/bin/bash

build_sawtooth_image () {
    BUILD_CMD="docker-compose -f docker-compose-installed.yaml build"
    $BUILD_CMD $1
    docker tag sawtooth-$1:latest remme/sawtooth-bare-$1:latest
    docker rmi sawtooth-$1:latest
}

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

# TODO set version in bare image
echo "Comparing the present and the required versions of Sawtooth..."
SAWTOOTH_BUILD_GIT_REF=$(docker run remme/sawtooth-validator:latest sh -c 'cat /git-ref' || true)
export SAWTOOTH_REPO_GIT_REF=$(git rev-parse HEAD:vendor/sawtooth-core)

if [ "$SAWTOOTH_BUILD_GIT_REF" != "$SAWTOOTH_REPO_GIT_REF" ]; then
    echo "Sawtooth version is different from the required one. Rebuilding..."

    echo "Cloning the Sawtooth repository..."
    # this is required because Sawtooth builds require th project dir to be a standalone Git repo
    git clone https://github.com/Remmeauth/sawtooth-core.git
    echo "Checking out the required tag..."
    cd sawtooth-core
    git checkout $SAWTOOTH_REPO_GIT_REF

    echo "Running Sawtooth rebuild..."
    build_sawtooth_image settings-tp
    build_sawtooth_image validator
    build_sawtooth_image rest-api
    build_sawtooth_image block-info-tp
    build_sawtooth_image devmode-rust

    echo "Doing cleanup..."
    cd ..
    rm -rf sawtooth-core
else
    echo "Found the required version build!"
fi

echo "Running REMME build..."
docker-compose $COMPOSE_FILES build
