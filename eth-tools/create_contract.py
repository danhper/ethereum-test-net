"""Creates a contract from the raw bytecode

Requires web3py to be installed

```
pip install web3
```

usage: python create_contract.py [-a ACCOUNT] [-v VALUE] [--ipc-path IPC_PATH] contract
"""

import argparse
import getpass
import os
from os import path
import sys

import web3


GETH_IPC_PATH = os.environ.get(
    "GETH_IPC_PATH", path.expanduser("~/.ethereum/geth.ipc"))

parser = argparse.ArgumentParser(prog="create-contract")
parser.add_argument(
    "contract", help="path to the file containing the contract")
parser.add_argument("-a", "--account", default=0, type=int,
                    help="Index of the account to use")
parser.add_argument("-v", "--value", default=0, type=int,
                    help="Value to send to the contract on creation")
parser.add_argument("--ipc-path", default=GETH_IPC_PATH,
                    help="Path to geth IPC (can be set with GETH_IPC_PATH env variable)")


def create_contract(args):
    with open(args["contract"]) as f:
        raw_contract = f.read()

    w3 = web3.Web3(web3.IPCProvider(args["ipc_path"]))
    if not w3.isConnected():
        raise RuntimeError("cound not connect to geth")

    account = w3.geth.personal.listAccounts()[args["account"]]
    password = getpass.getpass("Enter account password: ")
    w3.geth.personal.unlockAccount(account, password)

    result = w3.eth.sendTransaction({
        "from": account,
        "data": raw_contract,
        "value": args["value"],
    })

    receipt = w3.eth.waitForTransactionReceipt(result)

    print("Contract created at block {blockNumber} with address {contractAddress}".format(
        **receipt))


def main():
    args = parser.parse_args()
    try:
        create_contract(vars(args))
        return 0
    except Exception as ex:  # pylint: disable=broad-except
        print("Could not create contract: {0}".format(ex), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
