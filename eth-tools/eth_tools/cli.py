import argparse
import logging

from . import commands
from . import settings


parser = argparse.ArgumentParser(prog="transcation-generator")
parser.add_argument("-d", "--chain-data", help="directory for chain data",
                    default=settings.CHAIN_DATA_PATH)

subparsers = parser.add_subparsers(dest="command")

subparsers.add_parser("generate-transactions", help="generate random transactions")

subparsers.add_parser("generate-contract-calls", help="generate random contract calls")

start_miners_parser = subparsers.add_parser("start-miners", help="start all miners")
start_miners_parser.add_argument("-m", "--miners", help="list of miners", action="append")

stop_miners_parser = subparsers.add_parser("stop-miners", help="stop all miners")
stop_miners_parser.add_argument("-m", "--miners", help="list of miners", action="append")

subparsers.add_parser("list-nodes", help="list nodes in the cluster")

create_contract_parser = subparsers.add_parser("create-contract", help="creates a contract")
create_contract_parser.add_argument("contract", help="sol or json file with the contract")
create_contract_parser.add_argument("--node", help="node from which to create contract")
create_contract_parser.add_argument("--name", help="name of the contract. required when multiple "
                                                    "contracts exist in the same file")


def run():
    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()

    if not args.command:
        parser.error("no command provided")

    command = args.command.replace("-", "_")
    getattr(commands, command)(args)
