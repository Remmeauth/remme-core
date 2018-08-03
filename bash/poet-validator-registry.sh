eval `python3 /scripts/toml-to-env.py`

if [ "$REMME_CONSENSUS" = "poet-simulator" ]; then
    poet-validator-registry-tp -vv -C tcp://127.0.0.1:4004
fi
