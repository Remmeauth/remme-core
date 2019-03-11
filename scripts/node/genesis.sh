if [ -n "$INTEGRATION_TESTING" ]; then
    echo "Loading configuration..."
    python3 /project/scripts/loader.py
    source /config/network-config.env
fi

echo "Start mode: $REMME_START_MODE"

if [ "$REMME_START_MODE" = "genesis" ]; then
    echo "Generating genesis block..."
    if [ ! -e /genesis/batch ]; then
        mkdir /genesis/batch
    fi
    python3 -m remme.genesis
fi
