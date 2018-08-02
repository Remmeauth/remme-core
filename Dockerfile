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

# TODO check if it works with a newer version of Debian
FROM python:3.6.5-alpine as build
WORKDIR /root
RUN apk --update --no-cache add rsync pkgconf build-base autoconf automake libtool libffi-dev python3-dev zeromq-dev openssl-dev
RUN mkdir /install
ENV PYTHONUSERBASE=/install
COPY ./requirements.txt .
RUN pip3 install --user -r ./requirements.txt
COPY ./remme/rest_api/swagger-index.patch .
RUN cd $(python3 -c "import connexion, os; print(os.path.dirname(connexion.__file__) + '/vendor/swagger-ui')") && \
    sh update.sh 3.17.0 && \
    patch -p0 < /root/swagger-index.patch && \
    cd /root
RUN mkdir -p remme/remme
COPY ./remme ./remme/remme
COPY ./setup.py ./remme
RUN pip3 install --user ./remme
COPY ./tests ./tests
COPY ./bash /scripts

FROM alpine:edge as release
RUN apk --update --no-cache add --force python3 libffi openssl libzmq
COPY --from=build /install /install
ENV PYTHONUSERBASE=/install
COPY ./bash /scripts

FROM hyperledger/sawtooth-validator:1.0.1 as validator
COPY ./bash /scripts

FROM hyperledger/sawtooth-poet-validator-registry-tp:1.0.1 as validator-registry
COPY ./bash /scripts
