import argparse
import os

# from processor.remme_transaction_processor.token_handler import TokenHandler
from processor.protos.token_pb2 import Account

# TODO make address key with the TokenHandler prefix
# TODO fix readability issue from .pub file
# TODO remove b'' during formatting serialized proto to string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    parser.add_argument('key_file')
    args = parser.parse_args()

    account = Account()
    account.balance = args.token_supply

    assert(os.path.exists(args.key_file))
    with open(args.key_file, 'w+') as output_file:
        with open(args.key_address, 'r') as pub_key:
            key = args.key_address
            print('sawset proposal create {}={}'.format(key, account.SerializeToString()))