import argparse
from decimal import Decimal
import logging
import math
import os
from os import path
import random
import signal
import time
from typing import List

from web3 import Web3


INSECURE_PASSPHRASE = "foobarbaz"
TEN_YEARS_IN_SECONDS = 3600 * 24 * 365 * 10
MINERS = ["geth_node1", "aleth_node1"]

try:
    DATA_PATH = path.join(path.dirname(path.realpath(__file__)), "../data")
except NameError:
    # NOTE: for jupyter-like environment
    DATA_PATH = path.join(path.dirname(path.realpath(".")), "data")


class Node:
    def __init__(self, name, w3):
        self.name = name
        self.w3 = w3

    def __getattr__(self, key):
        return getattr(self.w3, key)

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

    @property
    def balance(self):
        balance = self.w3.eth.getBalance(self.address)
        return self.w3.fromWei(balance, "ether")

    @property
    def address(self):
        return self.w3.personal.listAccounts[0]

    @classmethod
    def from_file(cls, name, filename):
        # NOTE: instrumented version is very slow, so increase timeout
        provider = Web3.IPCProvider(filename, timeout=60 * 5)
        return cls(name, Web3(provider))


class NodeContainer:
    def __init__(self):
        self.nodes: List[Node] = []

    def add(self, node):
        self.nodes.append(node)

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
            ipc_file = path.join(root_dir, directory, "geth.ipc")
            if path.exists(ipc_file):
                self.add_node(Node.from_file(directory, ipc_file))

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
        for node in self.nodes:
            print("{0}: {1}".format(node.name, node.balance))

    def generate_random_transaction(self):
        # get a sender with money
        while True:
            sender = random.choice(self.nodes)
            if sender.balance > 0:
                break

        # get a recipient who is not the sender
        recipient = sender
        while recipient == sender:
            recipient = random.choice(self.nodes)

        # send between 1% and 40% of the balance (this is all made up)
        percentage_of_balance = Decimal(random.randint(1, 40)) / Decimal(100)
        value = math.ceil(Decimal(sender.balance) * percentage_of_balance)

        # TODO: fix values to get valid transactions
        sender.eth.sendTransaction({
            "to": recipient.address,
            "from": sender.address,
            "nonce": sender.eth.getTransactionCount(sender.address),
            "value": value,
        })


def stop_miners():
    manager = NodeManager()
    manager.add_nodes_from_dir(DATA_PATH)
    manager.stop_miners(MINERS)

def generate_transactions():
    manager = NodeManager()
    manager.add_nodes_from_dir(DATA_PATH)
    manager.initialize_nodes()
    manager.start_miners(MINERS)

    running = True

    def sigint_handler(_sig, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, sigint_handler)

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

    manager.stop_miners(MINERS)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(prog="transcation-generator")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("generate-transactions")
    subparsers.add_parser("stop-miners")

    args = parser.parse_args()
    if args.command == "stop-miners":
        stop_miners()
    else:
        generate_transactions()



if __name__ == "__main__":
    main()
