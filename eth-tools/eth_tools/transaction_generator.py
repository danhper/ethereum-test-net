import logging
import signal
import time
from typing import List, Any

from .node_manager import NodeManager
from .node import Node
from .contract import Contract
from .data_generator import DataGenerator


def generate_transactions(manager: NodeManager, miners: List[str]):
    manager.initialize_nodes()

    running = True

    def sigterm_handler(_sig, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, sigterm_handler)

    logging.info("starting to generate transactions")
    n = 0
    while running:
        try:
            manager.generate_random_transaction()
            time.sleep(1)
        except KeyboardInterrupt:
            running = False
        if n % 10 == 0:
            manager.print_balances()
        n = (n + 1) % 10


def generate_function_args(generator: DataGenerator, function_abi: dict) -> List[Any]:
    return [generator.generate_example(param["type"]) for param in function_abi["inputs"] if param]


def build_new_contract_transaction(node: Node, contract: Contract) -> dict:
    data_generator = DataGenerator(node)
    if contract.constructor_abi:
        args = generate_function_args(data_generator, contract.constructor_abi)
    else:
        args = []
    logging.info("creating contract with args %s", args)
    w3_contract = node.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
    return w3_contract.constructor(*args).buildTransaction()
