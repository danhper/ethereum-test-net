from .node_manager import NodeManager
from . import transaction_generator
from .contract import Contract


def stop_miners(args):
    manager = _get_manager(args)
    manager.stop_miners(args.miners)


def start_miners(args):
    manager = _get_manager(args)
    manager.initialize_nodes()
    manager.start_miners(args.miners)


def generate_transactions(args):
    manager = _get_manager(args)
    transaction_generator.generate_transactions(manager, args.miners)


def create_contract(args):
    manager = _get_manager(args)
    if args.node:
        node = manager.nodes[args.node]
    else:
        node = manager.get_random_node()
    contract = Contract.from_file(args.contract, contract_name=args.name)
    transaction = transaction_generator.build_new_contract_transaction(node, contract)
    node.create_contract(transaction, wait=True)


def _get_manager(args):
    manager = NodeManager()
    manager.add_nodes_from_dir(args.chain_data)
    return manager
