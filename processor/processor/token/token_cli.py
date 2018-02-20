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
from processor.rem_token.token_client import TokenClient

# TODO create decorator to remove manual changes to "commands"

class TokenCli(BasicCli):
    def __init__(self):
        self.client = TokenClient

    def parser_transfer(self, subparsers, parent_parser):
        message = 'Send REMME token transfer transaction.'

        parser = subparsers.add_parser(
            'transfer',
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

    def do_transfer(self, args):
        response = self.client.transfer(args.address_to, args.value)
        print(response)

    def main(self):
        commands = []
        commands += [({
            'parser': self.parser_transfer,
            'action': self.do_transfer
        })]
        self.main_wrapper(commands)

def main():
    TokenCli().main()