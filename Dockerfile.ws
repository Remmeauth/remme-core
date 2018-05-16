# FIXME: Wait until Sawtooth REST API is released as a separate package on PyPi
FROM hyperledger/sawtooth-rest-api:1.0.1
RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python3 python3-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev
WORKDIR /root
COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt
RUN mkdir -p remme/remme
COPY ./remme ./remme/remme
COPY ./setup.py ./remme
RUN pip3 install ./remme
COPY ./bash/.bashrc /root/.bashrc