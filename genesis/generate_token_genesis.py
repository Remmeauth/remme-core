import argparse
import os

# from processor.remme_transaction_processor.token_handler import TokenHandler
from processor.protos.token_pb2 import Account

OUTPUT_SH = 'genesis/token-proposal.sh'
OUTPUT_BATCH = '/genesis/token-proposal.batch'
SIGNING_KEY = '/root/.sawtooth/keys/my_key.priv'
KEY_FILE = 'keys/my_key.pub'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    args = parser.parse_args()

    account = Account()
    account.balance = int(args.token_supply)

    assert(os.path.exists(KEY_FILE))
    with open(OUTPUT_SH, 'w+') as output_file:
        with open(KEY_FILE, 'r') as pub_key:
            key = pub_key.read()
            # value = 'value'
            value = str(account.SerializeToString())[2:-1]
            output_file.write('sawset proposal create -o {} -k {} {}={} '.format(OUTPUT_BATCH, SIGNING_KEY, key[:-1], value))