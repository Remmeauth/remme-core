FROM sawtooth-validator:latest
RUN apt-get install -y software-properties-common && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD && \
    add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/bumper/stable xenial universe' && \
    apt-get update && \
    apt-get install -y python3-sawtooth-block-info
COPY ./scripts/node /scripts
