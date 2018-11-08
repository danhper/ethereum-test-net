import logging
import signal
import time
from typing import List

from .node_manager import NodeManager


def generate_transactions(manager: NodeManager, miners: List[str]):
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
