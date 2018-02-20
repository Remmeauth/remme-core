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
# ------------------------------------------------------------------------------

import argparse
import logging
import os
import sys
import traceback

import pkg_resources
from colorlog import ColoredFormatter

from processor.shared.exceptions import CliException, ClientException

DISTRIBUTION_NAME = 'sawtooth-intkey'

class BasicCli:
    def create_console_handler(self, verbose_level):
        clog = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
            "%(white)s%(message)s",
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            })

        clog.setFormatter(formatter)

        if verbose_level == 0:
            clog.setLevel(logging.WARN)
        elif verbose_level == 1:
            clog.setLevel(logging.INFO)
        else:
            clog.setLevel(logging.DEBUG)

        return clog


    def setup_loggers(self, verbose_level):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.create_console_handler(verbose_level))

    def create_parent_parser(self, prog_name):
        parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
        parent_parser.add_argument(
            '-v', '--verbose',
            action='count',
            help='enable more verbose output')

        try:
            version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
        except pkg_resources.DistributionNotFound:
            version = 'UNKNOWN'

        parent_parser.add_argument(
            '-V', '--version',
            action='version',
            version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
            .format(version),
            help='display version information')

        return parent_parser


    def create_parser(self, prog_name, parsers):
        parent_parser = self.create_parent_parser(prog_name)

        parser = argparse.ArgumentParser(
            parents=[parent_parser],
            formatter_class=argparse.RawDescriptionHelpFormatter)

        subparsers = parser.add_subparsers(title='subcommands', dest='command')

        for add_parser in parsers:
            add_parser(subparsers, parent_parser)

        return parser

    def main(self, commands, prog_name=os.path.basename(sys.argv[0]), args=None):
        if args is None:
            args = sys.argv[1:]
        parser = self.create_parser(prog_name, list(map(lambda command: command['parser'], commands)) )
        args = parser.parse_args(args)

        if args.verbose is None:
            verbose_level = 0
        else:
            verbose_level = args.verbose
        self.setup_loggers(verbose_level=verbose_level)

        if not args.command:
            parser.print_help()
            sys.exit(1)

        for command in commands:
            if args.command == command['name']:
                command['action'](args)
                return
        raise CliException("invalid command: {}".format(args.command))


    def main_wrapper(self, commands):
        # pylint: disable=bare-except
        try:
            self.main(commands)
        except (CliException, ClientException) as err:
            print("Error: {}".format(err), file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            pass
        except SystemExit as e:
            raise e
        except:
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)