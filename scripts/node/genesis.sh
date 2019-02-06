if [ "$NODEHOST" = "$GENESIS_HOST" ]; then
    REMME_START_MODE=genesis
else
    REMME_START_MODE=run
fi

if [ "$REMME_START_MODE" = "genesis" ]; then
    if [ ! -e /genesis/batch ]; then
        mkdir /genesis/batch
    fi
    python3 -m remme.genesis
fi
