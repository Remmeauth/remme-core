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

FROM alpine:3.8 as base
RUN apk --update --no-cache add --force python3=3.6.6-r0 libffi=3.2.1-r4 openssl=1.0.2o-r2 libzmq=4.2.3-r0
RUN mkdir /install
ENV PYTHONUSERBASE=/install
WORKDIR /root

FROM base as build
RUN apk --update --no-cache add rsync pkgconf build-base autoconf automake protobuf=3.5.2-r0 libtool=2.4.6-r5 libffi-dev=3.2.1-r4 python3-dev=3.6.6-r0 zeromq-dev=4.2.3-r0 openssl-dev=1.0.2o-r2
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install --user -r ./requirements.txt
COPY ./remme/rest_api/swagger-index.patch .
RUN cd $(python3 -c "import connexion, os; print(os.path.dirname(connexion.__file__) + '/vendor/swagger-ui')") && \
    sh update.sh 3.17.0 && \
    patch -p0 < /root/swagger-index.patch && \
    cd /root
COPY ./remme ./remme/remme
COPY ./protos ./remme/protos
RUN protoc -I=./remme/protos --python_out=./remme/remme/protos ./remme/protos/*.proto
COPY ./setup.py ./remme
RUN pip3 install --user ./remme
COPY ./tests ./tests
COPY ./bash /install/scripts/

FROM base as release
COPY --from=build /install /install

FROM hyperledger/sawtooth-validator:1.0.5 as validator
COPY ./bash /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM hyperledger/sawtooth-poet-validator-registry-tp:1.0.5 as validator-registry
COPY ./bash /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM hyperledger/sawtooth-block-info-tp:1.0.4 as sawtooth-block-info-tp
RUN apt-get update && \
    apt-get install patch
WORKDIR /
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
