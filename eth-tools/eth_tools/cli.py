import argparse
import logging

from . import commands
from . import settings


parser = argparse.ArgumentParser(prog="transcation-generator")
parser.add_argument("-d", "--chain-data", help="directory for chain data",
                    default=settings.CHAIN_DATA_PATH)
parser.add_argument("-m", "--miners", help="list of miners", action="append")

subparsers = parser.add_subparsers(dest="command")

subparsers.add_parser("generate-transactions")
subparsers.add_parser("stop-miners")
subparsers.add_parser("start-miners")


def run():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(prog="transcation-generator")
    parser.add_argument("-d", "--chain-data", help="directory for chain data",
                        default=settings.CHAIN_DATA_PATH)
    parser.add_argument("-m", "--miners", help="list of miners", action="append")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("generate-transactions")
    subparsers.add_parser("stop-miners")
    subparsers.add_parser("start-miners")

    args = parser.parse_args()
    if not args.miners:
        args.miners = settings.MINERS

    if not args.command:
        parser.error("no command provided")

    command = args.command.replace("-", "_")
    getattr(commands, command)(args)
