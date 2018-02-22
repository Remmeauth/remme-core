#!/usr/bin/env bash

sawtooth keygen key
cd ~/
python3 ./genesis/generate_token_genesis.py 10000
