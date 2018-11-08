import logging
import math
from os import path
from threading import Thread

from web3 import Web3
from filelock import FileLock

from . import settings


class Node:
    def __init__(self, name, w3):
        self.name = name
        self.w3 = w3
        self.last_transaction_block = self.w3.eth.blockNumber
        self._gas_price = self.w3.eth.gasPrice

    def __getattr__(self, key):
        return getattr(self.w3, key)

    def __repr__(self):
        return "Node(name='{0}')".format(self.name)

    def create_and_unlock_account(self):
        if not self.w3.personal.listAccounts:
            self.w3.personal.newAccount(settings.INSECURE_PASSPHRASE)
        account = self.w3.personal.listAccounts[0]
        # NOTE: aleth does not accept calls without duration
        self.w3.personal.unlockAccount(account, settings.INSECURE_PASSPHRASE,
                                       duration=settings.TEN_YEARS_IN_SECONDS)
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

    def get_wei_balance(self, address):
        return self.w3.eth.getBalance(address)

    def get_balance(self, address):
        return self.w3.fromWei(self.get_wei_balance(address), "ether")

    @property
    def balance(self):
        return self.get_balance(self.address)

    @property
    def wei_balance(self):
        return self.get_wei_balance(self.address)

    @property
    def address(self):
        return self.w3.personal.listAccounts[0]

    @classmethod
    def from_file(cls, name, filename):
        # NOTE: instrumented version is very slow, so increase timeout
        provider = Web3.IPCProvider(filename, timeout=60 * 5)
        return cls(name, Web3(provider))

    def get_nonce(self):
        return self.eth.getTransactionCount(self.address)

    def get_gas_price(self):
        # increase gas price if last transaction has not been mined yet
        if self.eth.blockNumber == self.last_transaction_block:
            self._gas_price *= 1.2
        else:
            self._gas_price = self.eth.gasPrice
        return math.ceil(self._gas_price)

    def _safe_send_transaction(self, transaction, update_last_transaction=False):
        try:
            result = self.eth.sendTransaction(transaction)
            if update_last_transaction:
                self.last_transaction_block = self.w3.eth.blockNumber
            return result
        except ValueError as ex:
            logging.error("failed to send transaction: {0} - {1}".format(ex, transaction))

    def send_ether(self, recipient, value):
        transaction = {
            "to": recipient.address,
            "from": self.address,
            "nonce": self.get_nonce(),
            "value": value,
            "gasPrice": self.get_gas_price(),
        }
        self._safe_send_transaction(transaction, update_last_transaction=True)

    def create_contract(self, bytecode):
        transaction = {
            "from": self.address,
            "gasPrice": self.get_gas_price(),
            "data": bytecode,
            "value": 100,
        }
        gas = self.eth.estimateGas(transaction)
        transaction["gas"] = gas
        tx_hash = self._safe_send_transaction(transaction)
        self._finalize_contract_creation(tx_hash)
        return tx_hash

    def wait_for_receipt(self, tx_hash):
        return self.w3.eth.waitForTransactionReceipt(tx_hash)

    def _finalize_contract_creation(self, tx_hash):
        def finalize():
            receipt = self.wait_for_receipt(tx_hash)
            self.process_receipt(receipt)
        Thread(target=finalize).start()

    def process_receipt(self, receipt):
        with FileLock(path.join(settings.DATA_PATH, "generated", "lock")):
            with open(path.join(settings.DATA_PATH, "generated", "addresses.txt"), "a") as f:
                print(receipt["contractAddress"], file=f)
