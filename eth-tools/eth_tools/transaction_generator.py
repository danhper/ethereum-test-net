from decimal import Decimal
import math
import logging
import signal
import time
import random
from typing import List, Any

from .node_manager import NodeManager
from .node import Node
from .contract import Contract
from .data_generator import DataGenerator


def generate_random_transaction(manager: NodeManager):
    node = manager.get_random_node()
    estimated_gas = node.eth.estimateGas({"value": 1})
    estimated_cost = estimated_gas * node.eth.gasPrice

    # get a sender with money
    while True:
        sender = manager.get_random_node()
        if sender.wei_balance > estimated_cost * 2:
            break

    # get a recipient who is not the sender
    recipient = sender
    while recipient == sender:
        recipient = manager.get_random_node()

    # send between 10% and 40% of the balance (this is all made up)
    percentage_of_balance = Decimal(random.randint(10, 40)) / Decimal(100)
    value = math.ceil(Decimal(sender.wei_balance) * percentage_of_balance)
    sender.send_ether(recipient, value)



def generate_transactions(manager: NodeManager):
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
            generate_random_transaction(manager)
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


def generate_random_contract_call(node: Node, contract: Contract, function_name=None):
    if not function_name:
        function_name = random.choice(contract.function_names)
    function_abi = contract.get_function_abi(function_name)
    data_generator = DataGenerator(node)
    args = generate_function_args(data_generator, function_abi)
