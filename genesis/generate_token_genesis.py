import argparse
import os

# from processor.remme_transaction_processor.token_handler import TokenHandler
from processor.protos.token_pb2 import Account

TOKEN_SUPPLY = 10000
GENESIS_COMMAND_FILE = 'genesis/genesis-proposal.txt'
PUB_KEY = '02e41e3bebe354903eaa5ce3dc6183a7575b00b5c265f516bbad7bc02418329e8e'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('key')
    args = parser.parse_args()

    account = Account()
    account.balance = TOKEN_SUPPLY

    assert(os.path.exists(args.key))
    with open(GENESIS_COMMAND_FILE, 'w+') as output_file:
        with open(args.key, 'r') as pub_key:
            # key = TokenHandler().make_address(PUB_KEY)
            key = PUB_KEY
            output_file.write('sawset proposal create {}={}'.format(key, account.SerializeToString()))