from os import path
import unittest


from eth_tools import settings
from eth_tools.contract import Contract


class ContractTest(unittest.TestCase):
    CONTRACT_DIR = path.join(settings.ROOT_DIR, "contracts")

    def test_from_sol_file(self):
        contract = self._load_contract("multi_owner_wallet.sol")
        self.assertIsNone(contract.address)
        self.assertEqual(contract.name, "Wallet")
    
    def test_constructor_abi(self):
        contract = self._load_contract("multi_owner_wallet.sol")
        self.assertEqual(len(contract.constructor_abi["inputs"]), 3)
        contract = self._load_contract("greeter.sol")
        self.assertEqual(len(contract.constructor_abi["inputs"]), 1)
    
    def test_get_function_abi(self):
        contract = self._load_contract("multi_owner_wallet.sol")
        abi = contract.get_function_abi("changeOwner")
        self.assertIsNotNone(abi)
        self.assertEqual(len(abi["inputs"]), 2)

    
    @classmethod
    def _load_contract(cls, filename):
        contract_file = path.join(cls.CONTRACT_DIR, filename)
        return Contract.from_file(contract_file)
