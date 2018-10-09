FROM remme/sawtooth-validator:latest as validator
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM remme/sawtooth-poet-validator-registry-tp:latest as validator-registry
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM remme/sawtooth-block-info-tp:latest as sawtooth-block-info-tp
RUN apt-get update && \
    apt-get install patch
WORKDIR /
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
