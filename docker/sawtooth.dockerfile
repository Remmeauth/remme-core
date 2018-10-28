FROM ubuntu:xenial
# TODO Change repo to bumper/stable when available
RUN apt-get update && \
    apt-get install -y software-properties-common patch && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 44FC67F19B2466EA && \
    add-apt-repository 'deb http://repo.sawtooth.me/ubuntu/bumper/nightly xenial universe' && \
    apt-get update && \
    apt-get install -y python3-sawtooth-block-info \
        python3-sawtooth-cli \
        python3-sawtooth-rest-api \
        python3-sawtooth-settings \
        python3-sawtooth-validator \
        sawtooth-devmode-rust
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
