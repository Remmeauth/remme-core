FROM alpine:3.8
WORKDIR /project/remme
RUN apk --update --no-cache add --force python3 libffi openssl libzmq && \
    pip3 install --upgrade pip && \
    pip3 install poetry
RUN apk --update --no-cache add rsync pkgconf build-base autoconf automake protobuf libtool libffi-dev python3-dev zeromq-dev openssl-dev
COPY ./pyproject.* ./
RUN poetry config settings.virtualenvs.create false && \
    poetry install
COPY ./remme ./remme
COPY ./protos ./protos
RUN protoc -I=./protos --python_out=./remme/protos ./protos/*.proto
COPY ./tests ./tests