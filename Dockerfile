FROM hyperledger/sawtooth-shell:1.0

RUN apt-get upgrade
RUN apt-get install -y python-setuptools