if [ "$REMME_START_MODE" = "genesis" ]; then
    if [ ! -f /root/.sawtooth/keys/key.priv ]; then
        sawtooth keygen key
    fi
    if [ ! -e /genesis/batch ]; then
        mkdir /genesis/batch
    fi
    python3 -m remme.genesis $REMME_TOKEN_SUPPLY
fi