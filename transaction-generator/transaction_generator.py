import argparse
from decimal import Decimal
import logging
import math
import os
from os import path
import random
import signal
import time
from threading import Thread
from typing import List

from filelock import FileLock
from web3 import Web3


INSECURE_PASSPHRASE = "foobarbaz"
TEN_YEARS_IN_SECONDS = 3600 * 24 * 365 * 10
# MINERS = ["geth_node1", "aleth_node1"]
MINERS = ["aleth_node1"]


try:
    ROOT_DIR = path.dirname(path.dirname(path.realpath(__file__)))
except NameError:
    # NOTE: for jupyter-like environment
    ROOT_DIR = path.dirname(path.realpath("."))

CHAIN_DATA_PATH = path.join(ROOT_DIR, "docker-data")
DATA_PATH = path.join(ROOT_DIR, "data")


class Node:
    def __init__(self, name, w3):
        self.name = name
        self.w3 = w3
        self.last_transaction_block = self.w3.eth.blockNumber
        self._gas_price = self.w3.eth.gasPrice

    def __getattr__(self, key):
        return getattr(self.w3, key)

    def __repr__(self):
        return "Node(name='{0}')".format(self.name)

    def create_and_unlock_account(self):
        if not self.w3.personal.listAccounts:
            self.w3.personal.newAccount(INSECURE_PASSPHRASE)
        account = self.w3.personal.listAccounts[0]
        # NOTE: aleth does not accept calls without duration
        self.w3.personal.unlockAccount(account, INSECURE_PASSPHRASE,
                                       duration=TEN_YEARS_IN_SECONDS)
        return account

    def initialize(self):
        logging.info("initializing {0}".format(self.name))
        account = self.create_and_unlock_account()
        self.miner.setEtherBase(account)

    def start_mining(self):
        logging.info("{0} starting to mine".format(self.name))
        self.w3.miner.start(1)

    def stop_mining(self):
        logging.info("{0} stopping to mine".format(self.name))
        self.w3.miner.stop()

    def get_wei_balance(self, address):
        return self.w3.eth.getBalance(address)

    def get_balance(self, address):
        return self.w3.fromWei(self.get_wei_balance(address), "ether")

    @property
    def balance(self):
        return self.get_balance(self.address)

    @property
    def wei_balance(self):
        return self.get_wei_balance(self.address)

    @property
    def address(self):
        return self.w3.personal.listAccounts[0]

    @classmethod
    def from_file(cls, name, filename):
        # NOTE: instrumented version is very slow, so increase timeout
        provider = Web3.IPCProvider(filename, timeout=60 * 5)
        return cls(name, Web3(provider))

    def get_nonce(self):
        return self.eth.getTransactionCount(self.address)

    def get_gas_price(self):
        # increase gas price if last transaction has not been mined yet
        if self.eth.blockNumber == self.last_transaction_block:
            self._gas_price *= 1.2
        else:
            self._gas_price = self.eth.gasPrice
        return math.ceil(self._gas_price)

    def _safe_send_transaction(self, transaction, update_last_transaction=False):
        try:
            result = self.eth.sendTransaction(transaction)
            if update_last_transaction:
                self.last_transaction_block = self.w3.eth.blockNumber
            return result
        except ValueError as ex:
            logging.error("failed to send transaction: {0} - {1}".format(ex, transaction))

    def send_ether(self, recipient, value):
        transaction = {
            "to": recipient.address,
            "from": self.address,
            "nonce": self.get_nonce(),
            "value": value,
            "gasPrice": self.get_gas_price(),
        }
        self._safe_send_transaction(transaction, update_last_transaction=True)

    def create_contract(self, bytecode):
        transaction = {
            "from": self.address,
            "gasPrice": self.get_gas_price(),
            "data": bytecode,
            "value": 100,
        }
        gas = self.eth.estimateGas(transaction)
        transaction["gas"] = gas
        tx_hash = self._safe_send_transaction(transaction)
        self._finalize_contract_creation(tx_hash)
        return tx_hash

    def wait_for_receipt(self, tx_hash):
        return self.w3.eth.waitForTransactionReceipt(tx_hash)

    def _finalize_contract_creation(self, tx_hash):
        def finalize():
            receipt = self.wait_for_receipt(tx_hash)
            self.process_receipt(receipt)
        Thread(target=finalize).start()

    def process_receipt(self, receipt):
        with FileLock(path.join(DATA_PATH, "generated", "lock")):
            with open(path.join(DATA_PATH, "generated", "addresses.txt"), "a") as f:
                print(receipt["contractAddress"], file=f)


class NodeContainer:
    def __init__(self):
        self.nodes: List[Node] = []

    def add(self, node):
        self.nodes.append(node)

    def __repr__(self):
        return "NodeContainer(nodes={0})".format(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.nodes[key]
        for w3 in self.nodes:
            if w3.name == key:
                return w3
        raise KeyError(key)



class NodeManager:
    def __init__(self):
        self.nodes = NodeContainer()

    def add_nodes_from_dir(self, root_dir):
        for directory in os.listdir(root_dir):
            dir_path = path.join(root_dir, directory)
            # XXX: this should probably be configurable
            paths = [path.join(dir_path, "geth.ipc"),
                     path.join(dir_path, "ethereum", "geth.ipc")]
            for ipc_file in paths:
                # NOTE: make sure we do not run into the 100 chars limit for sockets
                ipc_file = path.relpath(ipc_file, os.getcwd())
                if path.exists(ipc_file):
                    self.add_node(Node.from_file(directory, ipc_file))
                    break

    def add_node(self, node):
        self.nodes.add(node)

    def initialize_nodes(self):
        for node in self.nodes:
            node.initialize()

    def start_miners(self, miners):
        for miner in miners:
            self.nodes[miner].start_mining()

    def stop_miners(self, miners):
        for miner in miners:
            self.nodes[miner].w3.miner.stop()

    def print_balances(self):
        reporter = random.choice(self.nodes)
        block = reporter.eth.getBlock("latest")
        print("Balances at block {0} ({1}):".format(block.number, block.hash.hex()))
        for node in self.nodes:
            print("{0} ({1}): {2:.2f}".format(
                node.name, node.address, reporter.get_balance(node.address)))
        print("-" * 90)

    def generate_random_transaction(self):
        node = random.choice(self.nodes)
        estimated_gas = node.eth.estimateGas({"value": 1})
        estimated_cost = estimated_gas * node.eth.gasPrice

        # get a sender with money
        while True:
            sender = random.choice(self.nodes)
            if sender.wei_balance > estimated_cost * 2:
                break

        # get a recipient who is not the sender
        recipient = sender
        while recipient == sender:
            recipient = random.choice(self.nodes)

        # send between 10% and 40% of the balance (this is all made up)
        percentage_of_balance = Decimal(random.randint(10, 40)) / Decimal(100)
        value = math.ceil(Decimal(sender.wei_balance) * percentage_of_balance)
        sender.send_ether(recipient, value)


def stop_miners(chain_data_path, miners):
    manager = NodeManager()
    manager.add_nodes_from_dir(chain_data_path)
    manager.stop_miners(miners)


def start_miners(chain_data_path, miners):
    manager = NodeManager()
    manager.add_nodes_from_dir(chain_data_path)
    manager.start_miners(miners)


def generate_transactions(chain_data_path, miners):
    manager = NodeManager()
    manager.add_nodes_from_dir(chain_data_path)
    manager.initialize_nodes()
    manager.start_miners(miners)

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

    manager.stop_miners(miners)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(prog="transcation-generator")
    parser.add_argument("-d", "--chain-data", help="directory for chain data",
                        default=CHAIN_DATA_PATH)
    parser.add_argument("-m", "--miners", help="list of miners", action="append")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("generate-transactions")
    subparsers.add_parser("stop-miners")
    subparsers.add_parser("start-miners")

    args = parser.parse_args()
    if not args.miners:
        args.miners = MINERS

    if args.command == "stop-miners":
        stop_miners(args.chain_data, args.miners)
    elif args.command == "start-miners":
        start_miners(args.chain_data, args.miners)
    else:
        generate_transactions(args.chain_data, args.miners)



if __name__ == "__main__":
    main()
