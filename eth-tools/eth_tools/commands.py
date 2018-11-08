from .node_manager import NodeManager
from . import transaction_generator


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


def _get_manager(args):
    manager = NodeManager()
    manager.add_nodes_from_dir(args.chain_data)
    return manager
