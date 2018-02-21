FROM hyperledger/sawtooth-shell:1.0

RUN apt-get update
RUN apt-get install -y python3-pip
COPY requirements.txt /root
RUN pip3 install -r /root/requirements.txt