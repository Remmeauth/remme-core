FROM alpine:3.8
WORKDIR /project/remme
RUN apk --update --no-cache add --force bash python3 libffi openssl libzmq && \
    pip3 install --upgrade pip && \
    pip3 install poetry==0.12.10
COPY ./pyproject.* ./
COPY ./README.* ./
COPY ./remme ./remme
COPY ./protos ./protos
RUN apk --update --no-cache add --virtual .build_deps rsync pkgconf build-base autoconf automake protobuf libtool libffi-dev python3-dev zeromq-dev openssl-dev && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev && \
    protoc -I=./protos --python_out=./remme/protos ./protos/*.proto && \
    pip3 uninstall -y poetry && \
    rm -rf ./protos ./pyproject.* && \
    apk del .build_deps
COPY ./scripts/node /project/scripts
