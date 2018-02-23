# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

from processor.shared.basic_cli import BasicCli
from processor.token.token_client import TokenClient

# TODO create decorator to remove manual changes to "commands"
from processor.shared.exceptions import CliException, KeyNotFound

METHOD_TRANSFER = 'transfer'
METHOD_BALANCE = 'balance'
METHOD_ADDRESS = 'address'
class TokenCli(BasicCli):
    def __init__(self):
        self.client = TokenClient()

    def parser_transfer(self, subparsers, parent_parser):
        message = 'Send REMME token transfer transaction.'

        parser = subparsers.add_parser(
            METHOD_TRANSFER,
            parents=[parent_parser],
            description=message,
            help='Transfers <amount> of tokens to <address>.')

        parser.add_argument(
            'address_to',
            type=str,
            help='REMME account address.')

        parser.add_argument(
            'value',
            type=int,
            help='Amount of REMME tokens to transfer with 4 decimals.')
    def parser_balance(self, subparsers, parent_parser):
        message = 'Show address balance.'

        parser = subparsers.add_parser(
            METHOD_BALANCE,
            parents=[parent_parser],
            description=message,
            help='Balance of <address>.')

        parser.add_argument(
            'address',
            type=str,
            help='Check address. Specify "me" to use your address.')

    def parser_address(self, subparsers, parent_parser):
        message = 'Show current address or make one from public key.'

        parser = subparsers.add_parser(
            METHOD_ADDRESS,
            parents=[parent_parser],
            description=message,
            help='You may specify "me" instead of a public key.')

        parser.add_argument(
            'pub_key',
            type=str,
            help='Type "me" or public address from which to show address in REMME network')

    def do_address(self, args):
        public_key = args.pub_key
        if public_key == 'me':
            public_key = self.client._signer.get_public_key().as_hex()
        if not int(public_key, 16) or len(public_key) != 66:
            raise CliException('Please, make sure public key is a 66 digit hex number: {}'.format(public_key))
        print(self.client.make_address(public_key))

    def do_transfer(self, args):
        response = self.client.transfer(address_to=args.address_to, value=args.value)
        print(response)
    def do_balance(self, args):
        if args.address == 'me':
            args.address = self.client.make_address(self.client._signer.get_public_key().as_hex())
        try:
            account = self.client.get_account(address=args.address)
            print("Balance: {}\n".format(account.balance))
        except KeyNotFound:
            print('Balance: 0 REM')
        except Exception as e:
            print(e)


    def init(self):
        commands = []
        commands += [{
            'name': METHOD_TRANSFER,
            'parser': self.parser_transfer,
            'action': self.do_transfer
        },
        {
            'name': METHOD_BALANCE,
            'parser': self.parser_balance,
            'action': self.do_balance
        },
        {
            'name': METHOD_ADDRESS,
            'parser': self.parser_address,
            'action': self.do_address
        }
        ]
        self.main_wrapper(commands)

def main():
    TokenCli().init()