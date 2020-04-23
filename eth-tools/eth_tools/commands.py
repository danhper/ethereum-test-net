import json

from . import settings
from . import transaction_sender
from .node_manager import NodeManager


def stop_miners(args):
    manager = _get_manager(args)
    manager.stop_miners(_get_miners(args))


def start_miners(args):
    manager = _get_manager(args)
    manager.start_miners(_get_miners(args))


def generate_transactions(args):
    manager = _get_manager(args)
    transaction_sender.generate_transactions(manager)


def list_nodes(args):
    manager = _get_manager(args)
    for node in manager.nodes:
        print(node.name)


def create_contract(args):
    manager = _get_manager(args)
    if args.node:
        node = manager.nodes[args.node]
    else:
        node = manager.get_random_node()
    transaction_sender.create_contract(manager, node, args.contract, args.name)


def generate_contract_calls(args):
    manager = _get_manager(args)
    transaction_sender.generate_contract_calls(manager)


def list_transactions(args):
    manager = _get_manager(args)
    node = manager.get_random_node()
    result = list(node.list_all_transactions())
    if args.output:
        with open(args.output) as f:
            json.dump(result, f)
    else:
        print(json.dumps(result))


def _get_manager(args):
    manager = NodeManager()
    manager.add_nodes_from_dir(args.chain_data)
    return manager


def _get_miners(args):
    if args.miners:
        return args.miners
    return settings.MINERS
