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
        for node in self.nodes:
            if node.name == key:
                return node
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
            self.nodes[miner].initialize()
            self.nodes[miner].start_mining()

    def stop_miners(self, miners):
        for miner in miners:
            self.nodes[miner].stop_mining()

    def print_balances(self):
        reporter = random.choice(self.nodes)
        block = reporter.eth.getBlock("latest")
        print("Balances at block {0} ({1}):".format(block.number, block.hash.hex()))
        for node in self.nodes:
            print("{0} ({1}): {2:.2f}".format(
                node.name, node.address, reporter.get_balance(node.address)))
        print("-" * 90)

    def get_random_node(self):
        return random.choice(self.nodes)
