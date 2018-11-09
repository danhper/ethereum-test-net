from .node_manager import NodeManager
from . import transaction_generator
from . import settings
from .contract import Contract


def stop_miners(args):
    manager = _get_manager(args)
    manager.stop_miners(_get_miners(args))


def start_miners(args):
    manager = _get_manager(args)
    manager.start_miners(_get_miners(args))


def generate_transactions(args):
    manager = _get_manager(args)
    transaction_generator.generate_transactions(manager)


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
    node.initialize()
    contract = Contract.from_file(args.contract, contract_name=args.name)
    transaction = transaction_generator.build_new_contract_transaction(node, contract)
    node.create_contract(contract, transaction, wait=True)


def _get_manager(args):
    manager = NodeManager()
    manager.add_nodes_from_dir(args.chain_data)
    return manager

def _get_miners(args):
    if args.miners:
        return args.miners
    return settings.MINERS
