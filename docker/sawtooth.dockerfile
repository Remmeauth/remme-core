FROM remme/sawtooth-bare-block-info-tp:latest as sawtooth-block-info-tp
RUN apt-get update && \
    apt-get install patch
WORKDIR /
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch

FROM remme/sawtooth-bare-validator:latest as validator
# This piece of magic is required to get the BlockInfo tx family to work since it is not included
COPY --from=sawtooth-block-info-tp /tmp/python3-sawtooth-block-info*.deb /tmp
RUN echo "deb http://repo.sawtooth.me/ubuntu/ci xenial universe" >> /etc/apt/sources.list \
    && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD \
    || apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 8AA7AF1F1091A5FD) \
    && apt-get update \
    && dpkg -i /tmp/python3-sawtooth-block-info*.deb || true \
    && apt-get -f -y install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py
