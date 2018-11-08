from decimal import Decimal
import math
import os
from os import path
import random
from typing import List

from .node import Node


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

