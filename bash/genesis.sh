if [ "$REMME_START_MODE" = "genesis" ]; then
    if [ ! -f /etc/sawtooth/keys/validator.priv ]; then
        sawtooth keygen key
    fi
    if [ ! -e /genesis/batch ]; then
        mkdir /genesis/batch
    fi
    python3 -m remme.genesis
fi