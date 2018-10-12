FROM hyperledger/sawtooth-validator:1.0.5 as validator
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM hyperledger/sawtooth-poet-validator-registry-tp:1.0.5 as validator-registry
COPY ./scripts/node /scripts
RUN chmod +x /scripts/toml-to-env.py

FROM hyperledger/sawtooth-block-info-tp:1.0.4 as sawtooth-block-info-tp
RUN apt-get update && \
    apt-get install patch
WORKDIR /
COPY ./blockinfo_fix.patch /blockinfo_fix.patch
RUN patch -p0 < /blockinfo_fix.patch
