from decimal import Decimal
from functools import lru_cache
import json
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
from . import settings


def build_send_ether_transaction(manager: NodeManager):
    node = manager.get_random_node()
    estimated_gas = node.eth.estimateGas({"value": 1, "from": node.address})
    estimated_cost = estimated_gas * node.eth.gasPrice

    # get a sender with money
    while True:
        sender = manager.get_random_address()
        if node.get_wei_balance(sender) > estimated_cost * 2:
            break

    # get a recipient who is not the sender
    recipient = sender
    while recipient == sender:
        recipient = manager.get_random_address()

    # send between 10% and 40% of the balance (this is all made up)
    percentage_of_balance = Decimal(random.randint(10, 40)) / Decimal(100)
    value = math.ceil(Decimal(node.get_wei_balance(sender)) * percentage_of_balance)
    return {
        "to": recipient,
        "from": sender,
        "nonce": node.get_nonce(sender),
        "value": value,
        "gasPrice": node.get_gas_price(),
    }


def make_function_args(generator: DataGenerator, function_abi: dict) -> List[Any]:
    return [generator.generate_example(param["type"]) for param in function_abi["inputs"] if param]


def build_new_contract_transaction(node: Node, contract: Contract) -> dict:
    data_generator = DataGenerator(node)
    if contract.constructor_abi:
        args = make_function_args(data_generator, contract.constructor_abi)
    else:
        args = []
    logging.info("creating contract with args %s", args)
    w3_contract = node.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
    return w3_contract.constructor(*args).buildTransaction()


@lru_cache()
def _search_contract(contract_name: str, contracts_file: str = settings.CONTRACTS_FILE) -> Contract:
    with open(contracts_file) as f:
        for line in f:
            contract_data = json.loads(line)
            if contract_data["name"] == contract_name:
                return Contract(**contract_data)
    raise ValueError("{0} not found".format(contract_name))


def build_contract_call_transaction(node: Node, contract_name: str, function_name=None):
    contract = _search_contract(contract_name)
    if not function_name:
        function_name = random.choice(contract.function_names)
    function_abi = contract.get_function_abi(function_name)
    data_generator = DataGenerator(node)
    w3_contract = node.eth.contract(abi=contract.abi, address=contract.address)
    w3_function = w3_contract.get_function_by_name(function_name)
    args = make_function_args(data_generator, function_abi)
    logging.info("creating contract call to %s with args %s", function_name, args)
    return w3_function(*args).buildTransaction()
