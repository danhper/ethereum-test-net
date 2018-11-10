import json
import logging
import random
import signal
import time

from . import transaction_builder
from . import settings
from .contract import Contract
from .util import interruptible_infinite_loop
from .node_manager import NodeManager, Node


def generate_transactions(manager: NodeManager):
    manager.initialize_nodes()
    logging.info("starting to generate transactions")

    @interruptible_infinite_loop(sleep=1, log_func=lambda _: manager.print_balances())
    def run():
        transaction = transaction_builder.build_send_ether_transaction(manager)
        node = manager.node_by_address(transaction["from"])
        node.safe_send_transaction(transaction, update_last_transaction=True)

    run()


def create_contract(manager: NodeManager, node: Node, contract_file: str, contract_name: str):
    node.initialize()
    contract = Contract.from_file(contract_file, contract_name=contract_name)
    transaction = transaction_builder.build_new_contract_transaction(node, contract)
    node.create_contract(contract, transaction, wait=True)


def generate_contract_calls(manager: NodeManager):
    manager.initialize_nodes()
    logging.info("starting to generate contract transactions")
    with open(settings.CONTRACTS_FILE) as f:
        contract_names = list({json.loads(line)["name"] for line in f})

    @interruptible_infinite_loop(sleep=1)
    def run():
        node = manager.get_random_node()
        contract_name = random.choice(contract_names)
        transaction = transaction_builder.build_contract_call_transaction(node, contract_name)
        transaction["from"] = node.address
        node.safe_send_transaction(transaction)

    run()
