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

FROM ubuntu:xenial AS development
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD && \
    echo "deb http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y sawtooth && \
    apt-get install -y python3-pip && \
    apt-get install -y libssl-dev
WORKDIR /root
COPY ./bash/.bashrc /root/.bashrc
RUN mkdir remme
COPY . ./remme
RUN pip3 install -r ./remme/requirements.txt
RUN pip3 install ./remme
