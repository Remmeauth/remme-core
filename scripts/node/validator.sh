# TODO add BlockInfo back when new Sawtooth implementation stabilizes

eval `python3 /scripts/toml-to-env.py`

ADDITIONAL_ARGS=""

echo "Economy enabled: $REMME_ECONOMY_ENABLED"

if [ ! -f /etc/sawtooth/keys/validator.priv ]; then
    sawadm keygen
fi

if [ "$REMME_START_MODE" = "genesis" ]; then
    if [ -d /var/lib/sawtooth ]; then
        rm /var/lib/sawtooth/*
    fi

    sawset genesis -k /etc/sawtooth/keys/validator.priv
    GENESIS_BATCHES="config-genesis.batch"

    if [ "$REMME_CONSENSUS" = "devmode" ]; then
        sawset proposal create \
            -k /etc/sawtooth/keys/validator.priv \
            sawtooth.consensus.min_wait_time=5 \
            -o devmode.batch

        GENESIS_BATCHES="$GENESIS_BATCHES devmode.batch"
    fi

    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        "remme.settings.pub_key_encryption=$(cat /etc/sawtooth/keys/validator.pub)" \
        "remme.settings.genesis_owners=$(cat /etc/sawtooth/keys/validator.pub)" \
        "remme.settings.storage_pub_key=$(cat /etc/sawtooth/keys/validator.pub)" \
        remme.settings.swap_comission=100 \
        -o settings_config.batch

    GENESIS_BATCHES="$GENESIS_BATCHES settings_config.batch"

    if [ "$REMME_ECONOMY_ENABLED" = "True" ]; then
        GENESIS_BATCHES="$GENESIS_BATCHES /genesis/batch/token-proposal.batch"
    fi

    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        sawtooth.validator.batch_injectors=block_info \
        "sawtooth.validator.block_validation_rules=NofX:1,block_info;XatY:block_info,0;local:0" \
        -o block_info_config.batch
    
    GENESIS_BATCHES="$GENESIS_BATCHES block_info_config.batch"

    sawadm genesis $GENESIS_BATCHES
fi

if [ "$REMME_START_MODE" = "run" ] && [ -s "/config/seeds-list.txt" ]; then
    SEEDS=$(sed ':a;N;$!ba;s/\n/,/g' /config/seeds-list.txt)
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --seeds $SEEDS --peers $SEEDS"
fi

sawtooth-validator -vv \
    --endpoint tcp://$REMME_VALIDATOR_IP:$REMME_VALIDATOR_PORT \
    --bind component:tcp://127.0.0.1:4004 \
    --bind consensus:tcp://127.0.0.1:5005 \
    --bind network:tcp://0.0.0.0:8800 \
    $ADDITIONAL_ARGS
