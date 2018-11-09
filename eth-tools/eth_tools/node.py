import logging
import math
from os import path
from threading import Thread

from web3 import Web3
from filelock import FileLock

from . import settings
from .contract import Contract


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

    def create_contract(self, transaction: dict, wait=False, callback=None):
        transaction = transaction.copy()
        transaction["from"] = self.address
        tx_hash = self._safe_send_transaction(transaction)
        return self._finalize_contract_creation(tx_hash, wait=wait, callback=callback)

    def wait_for_receipt(self, tx_hash):
        return self.w3.eth.waitForTransactionReceipt(tx_hash)

    def _finalize_contract_creation(self, tx_hash, wait=False, callback=None):
        def finalize():
            receipt = self.wait_for_receipt(tx_hash)
            self.process_receipt(receipt)
            if callback:
                callback(receipt)
            return receipt

        if wait:
            return finalize()
        else:
            thread = Thread(target=finalize)
            thread.start()
            return None

    def process_receipt(self, receipt):
        addresses_path = path.join(settings.DATA_PATH, "generated", "addresses.txt")
        with FileLock(path.join(settings.DATA_PATH, "generated", "lock")):
            with open(addresses_path, "a") as f:
                print(receipt["contractAddress"], file=f)
        logging.info("%s created contract at address %s, address saved in %s",
                     self.name, receipt["contractAddress"], addresses_path)

    def list_all_accounts(self):
        block = self.w3.eth.getBlock("latest")
        accounts = set()
        while True:
            if int(block.miner, 16) != 0:
                accounts.add(block.miner)
            for tx_hash in block.transactions:
                transaction = self.w3.eth.getTransaction(tx_hash)
                accounts.add(transaction["from"])
                if transaction.get("to"):
                    accounts.add(transaction["to"])
            if int(block.parentHash.hex(), 16) == 0:
                break
            block = self.w3.eth.getBlock(block.parentHash)
        return accounts
