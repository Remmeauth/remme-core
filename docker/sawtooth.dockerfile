FROM ubuntu:xenial
# TODO Change repo to bumper/stable when available
RUN apt-get update && \
    apt-get install -y software-properties-common patch && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD && \
    add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/bumper/stable xenial universe' && \
    apt-get update && \
    apt-get install -y python3-sawtooth-block-info \
        python3-sawtooth-cli \
        python3-sawtooth-rest-api \
        python3-sawtooth-settings \
        python3-sawtooth-validator \
        sawtooth-devmode-engine-rust
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
