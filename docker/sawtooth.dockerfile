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
RUN apt-get install curl apt-transport-https && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y kubectl
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
