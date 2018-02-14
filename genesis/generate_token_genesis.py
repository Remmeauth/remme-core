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
    parser.add_argument('output_file')
    args = parser.parse_args()

    account = Account()
    account.balance = int(args.token_supply)

    assert(os.path.exists(args.key_file))
    with open(args.output_file, 'w+') as output_file:
        with open(args.key_file, 'r') as pub_key:
            key = pub_key.read()
            output_file.write('sawset proposal create {}={}'.format(key[:-1], str(account.SerializeToString())[2:-1]))