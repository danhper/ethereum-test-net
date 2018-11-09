import unittest
from unittest.mock import Mock


from eth_tools.data_generator import DataGenerator


class DataGeneratorText(unittest.TestCase):
    def setUp(self):
        self._all_addresses = {
            "0x91dB30D3Cc94065537604C4787EcDF74af5b079d",
            "0x6FBB99F2B07af5a7c3a227871219d76Df767F097"
        }
        node = Mock(**{"list_all_accounts.return_value": self._all_addresses})
        self.data_generator = DataGenerator(node)

    def test_address_example(self):
        address = self.data_generator.generate_example("address")
        self.assertEqual(len(address), 42)
        self.assertIn(address, self._all_addresses)

    def test_list_example(self):
        for _ in range(5):
            addresses = self.data_generator.generate_example("address[]")
            self.assertIsInstance(addresses, list)
            if addresses:
                self.assertIn(addresses[0], self._all_addresses)

    def test_binary_example(self):
        self.assertIsInstance(self.data_generator.generate_example("bytes"), bytes)
