#!/bin/bash

echo "Node settings:"
cat /config/network-config.env

source /config/network-config.env

ADDITIONAL_ARGS=""

if [ ! -f /etc/sawtooth/keys/validator.priv ]; then
    echo "validator key pair not found - creating a new one..."
    sawadm keygen
fi

echo "Node public key $(cat /etc/sawtooth/keys/validator.pub)"

if [ "$REMME_START_MODE" = "genesis" ]; then
    echo "Building the genesis block..."

    if [ -d /var/lib/sawtooth ]; then
        echo "Cleaning up blockchain database..."
        rm /var/lib/sawtooth/*
    fi

    echo "Generating initial settings..."
    sawset genesis -k /etc/sawtooth/keys/validator.priv
    GENESIS_BATCHES="config-genesis.batch"

    echo "Generating permissioning settings..."
    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        sawtooth.identity.allowed_keys="$(cat /etc/sawtooth/keys/validator.pub)" \
        -o permissioning_setup.batch
    GENESIS_BATCHES="$GENESIS_BATCHES permissioning_setup.batch"

    sawtooth identity policy create \
        -k /etc/sawtooth/keys/validator.priv \
        node_account_permissions_policy "PERMIT_KEY $(cat /etc/sawtooth/keys/validator.pub)" \
        -o node_account_permissions_policy.batch
    GENESIS_BATCHES="$GENESIS_BATCHES node_account_permissions_policy.batch"

    sawtooth identity role create \
        -k /etc/sawtooth/keys/validator.priv \
        transactor.transaction_signer.node_account node_account_permissions_policy \
        -o node_account_permissions_role.batch
    GENESIS_BATCHES="$GENESIS_BATCHES node_account_permissions_role.batch"

    echo "REMME consensus is set to use. Writing consensus specific settings..."
    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        remme.consensus.voters_number=1 \
        remme.consensus.timing=10 \
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
        remme.settings.min_share=0.45 \
        remme.settings.unfreeze_bonus=10 \
        -o settings_config.batch

    GENESIS_BATCHES="$GENESIS_BATCHES settings_config.batch"

    echo "Economy model is enabled. Writing the batch to enable it..."
    GENESIS_BATCHES="$GENESIS_BATCHES /genesis/batch/token-proposal.batch"

    echo "Writing batch for node account genesis..."
    GENESIS_BATCHES="$GENESIS_BATCHES /genesis/batch/node-proposal.batch"

    echo "Writing batch for node 2 master node convertion genesis..."
    GENESIS_BATCHES="$GENESIS_BATCHES /genesis/batch/n2mn-proposal.batch"

    echo "Writing batch for consensus account genesis..."
    GENESIS_BATCHES="$GENESIS_BATCHES /genesis/batch/consensus-proposal.batch"

    echo "Writing batch injector settings..."
    sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        "sawtooth.validator.batch_injectors=remme_batches" \
        "sawtooth.validator.block_validation_rules=NofX:1,block_info;XatY:block_info,0;local:0;NofX:1,consensus_account;XatY:consensus_account,1;local:0;NofX:1,obligatory_payment;XatY:obligatory_payment,2;local:0;NofX:1,bet;XatY:bet,3;local:0" \
        -o block_info_config.batch

    GENESIS_BATCHES="$GENESIS_BATCHES block_info_config.batch"

    echo "Generating genesis block..."
    sawadm genesis $GENESIS_BATCHES

    echo "Genesis block generated!"
fi

if [ -n "$SEEDS_LIST" ]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --peering static --peers $SEEDS_LIST"
elif [ "$REMME_START_MODE" = "run" ] && [ -s "/config/seeds-list.txt" ]; then
    echo "Gettings the seeds list..."
    SEEDS=$(sed ':a;N;$!ba;s/\n/,/g' /config/seeds-list.txt)
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --seeds $SEEDS --peers $SEEDS"
fi

echo "Starting the validator..."
sawtooth-validator -vv \
    --endpoint tcp://$REMME_VALIDATOR_IP:8800 \
    --bind component:tcp://127.0.0.1:4004 \
    --bind consensus:tcp://127.0.0.1:5005 \
    --bind network:tcp://0.0.0.0:8800 \
    $ADDITIONAL_ARGS
