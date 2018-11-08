import unittest


from eth_tools import data_generator


class DataGeneratorText(unittest.TestCase):
    def test_address_example(self):
        address = data_generator.generate_example("address")
        self.assertEqual(len(address), 40)
        for char in address:
            self.assertTrue(char.isalnum())

    def test_list_example(self):
        for _ in range(5):
            addresses = data_generator.generate_example("address[]")
            self.assertIsInstance(addresses, list)
            if addresses:
                self.assertEqual(len(addresses[0]), 40)

    def test_binary_example(self):
        self.assertIsInstance(data_generator.generate_example("bytes"), bytes)
