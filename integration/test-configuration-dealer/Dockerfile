FROM python:3.6
RUN apt-get update && apt-get install -y libsecp256k1-dev 
RUN pip3 install sawtooth_signing aiohttp
COPY dealer.py dealer.py
ENTRYPOINT [ "python3", "dealer.py" ]
