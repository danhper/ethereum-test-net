import os
from os import path


INSECURE_PASSPHRASE = "foobarbaz"
TEN_YEARS_IN_SECONDS = 3600 * 24 * 365 * 10
MINERS = ["geth_node1", "aleth_node1"]


ROOT_DIR = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))
CHAIN_DATA_PATH = os.environ.get(
    "CHAIN_DATA_PATH",
    path.join(path.expanduser("~/.eth-docker-data")))
DATA_PATH = path.join(ROOT_DIR, "data")

CONTRACTS_FILE = path.join(DATA_PATH, "generated", "contracts.jsonl")
