# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

# contains only those dependencies which are common for all other stages
FROM alpine:3.8 as base
ENV INSTALL_DIR=/projects/install
ENV PYTHONUSERBASE=$INSTALL_DIR
RUN apk --update --no-cache add --force python3 libffi openssl libzmq

# setting up dependencies required for install binaries and contains application source code
FROM base as build-common
RUN apk --update --no-cache add rsync pkgconf build-base autoconf automake protobuf libtool libffi-dev python3-dev zeromq-dev openssl-dev && \
    pip3 install --upgrade pip && \
    pip3 install poetry
ENV PROJECT_DIR=/projects/remme
WORKDIR $PROJECT_DIR
COPY ./pyproject.toml .
COPY ./remme ./remme
COPY ./protos ./protos
RUN protoc -I=./protos --python_out=./remme/protos ./protos/*.proto && \
    poetry config settings.virtualenvs.in-project true

# used for running tests on the project
FROM build-common as test
COPY ./tests ./tests
RUN poetry install

# the intermediate stage that builds dependencies for the release image
FROM build-common as build-release
COPY ./README.rst ./README.rst
RUN mkdir -p $INSTALL_DIR && \
    poetry build --format=wheel --no-interaction && \
    pip3 install --user --ignore-installed ./dist/*.whl

FROM base as release
COPY --from=build-release $INSTALL_DIR $INSTALL_DIR
RUN mkdir -p /projects/scripts
COPY ./scripts/node /projects/scripts

FROM hyperledger/sawtooth-validator:1.0.5 as validator
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM hyperledger/sawtooth-poet-validator-registry-tp:1.0.5 as validator-registry
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM hyperledger/sawtooth-block-info-tp:1.0.4 as sawtooth-block-info-tp
RUN apt-get update && \
    apt-get install patch
WORKDIR /
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
