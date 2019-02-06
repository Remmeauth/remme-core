#!/usr/bin/env bash
ADDITIONAL_ARGS=""

echo "Genesis host is $GENESIS_HOST"

if [ "$NODEHOST" = "$GENESIS_HOST" ]; then
    REMME_START_MODE=genesis
    echo "Generating genesis block on $NODEHOST..."
else
    REMME_START_MODE=run
    echo "Starting a simple node at $NODEHOST..."
fi

if [ ! -f /etc/sawtooth/keys/validator.priv ]; then
    echo "validator key pair not found - creating a new one..."
    sawadm keygen
fi

if [ "$REMME_START_MODE" = "genesis" ]; then
    echo "Building the genesis block..."

    if [ -d /var/lib/sawtooth ]; then
        echo "Cleaning up blockchain database..."
        rm /var/lib/sawtooth/*
    fi

    echo "Generating initial settings..."
    sawset genesis -k /etc/sawtooth/keys/validator.priv
    GENESIS_BATCHES="config-genesis.batch"

    echo "REMME consensus is set to use. Writing consensus specific settings..."
    sawset proposal create \
    -k /etc/sawtooth/keys/validator.priv \
        remme.consensus.voters_number=1 \
        remme.consensus.timing=3 \
        remme.consensus.allowed_validators="$(cat /etc/sawtooth/keys/validator.pub)" \
        -o consensus.batch

    GENESIS_BATCHES="$GENESIS_BATCHES consensus.batch"

    echo "Writing REMME settings..."
    echo "Writing out validator public key: "
    cat /etc/sawtooth/keys/validator.pub
    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        "remme.settings.pub_key_encryption=$(cat /etc/sawtooth/keys/validator.pub)" \
        "remme.settings.genesis_owners=$(cat /etc/sawtooth/keys/validator.pub)" \
        remme.settings.swap_comission=100 \
        remme.settings.committee_size=10 \
        remme.settings.blockchain_size=300 \
        remme.settings.obligatory_payment=1 \
        remme.settings.transaction_fee=0.0010 \
        remme.settings.blockchain_tax=0.1 \
        remme.settings.minimum_stake=250000 \
        remme.settings.minimum_bet=10000 \
        -o settings_config.batch

    GENESIS_BATCHES="$GENESIS_BATCHES settings_config.batch"

    echo "Economy model is enabled. Writing the batch to enable it..."
    GENESIS_BATCHES="$GENESIS_BATCHES /genesis/batch/token-proposal.batch"

    echo "Writing batch injector settings..."
    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        sawtooth.validator.batch_injectors=block_info \
        "sawtooth.validator.block_validation_rules=NofX:1,block_info;XatY:block_info,0;local:0" \
        -o block_info_config.batch

    GENESIS_BATCHES="$GENESIS_BATCHES block_info_config.batch"

    echo "Generating genesis block..."
    sawadm genesis $GENESIS_BATCHES

    echo "Genesis block generated!"
fi

SEEDS_LIST=$(kubectl get pods -l role=remme-node -o jsonpath="{.items[*].status.podIP}" | sed -E "s/([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)/tcp:\/\/\1\-\2-\3-\4.default\.pod\.cluster\.local:8800/g" | sed "s/ /,/g")
ADDITIONAL_ARGS="$ADDITIONAL_ARGS --peers $SEEDS_LIST"

echo "Seeds list is $SEEDS_LIST"

VALIDATOR_HOST=$(echo $PODIP | sed -E "s/([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)/\1\-\2-\3-\4.default\.pod\.cluster\.local/g")

echo "Starting the validator..."
sawtooth-validator -vv \
    --endpoint tcp://$VALIDATOR_HOST:8800 \
    --bind component:tcp://127.0.0.1:4004 \
    --bind consensus:tcp://127.0.0.1:5005 \
    --bind network:tcp://0.0.0.0:8800 \
    $ADDITIONAL_ARGS
