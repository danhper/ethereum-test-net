from os import path
import unittest
from unittest.mock import Mock

from eth_tools.node_manager import NodeManager, Node, NodeContainer
from eth_tools import settings


def make_dummy_address(name):
    return hex(hash(name))


def make_mock_node(name, _ipc_file=None):
    m = Mock()
    m.name = name
    m.address = make_dummy_address(name)
    return m


class NodeManagerTest(unittest.TestCase):
    FIXTURES_DIR = path.join(settings.ROOT_DIR, "eth-tools", "tests", "fixtures")

    def setUp(self):
        Node.from_file = make_mock_node
        self.manager = NodeManager()
        self.manager.add_nodes_from_dir(path.join(self.FIXTURES_DIR, "nodes-root"))

    def test_add_nodes_from_dir(self):
        self.assertEqual(len(self.manager.nodes), 2)
        names = {node.name for node in self.manager.nodes}
        self.assertEqual(names, {"foo", "bar"})
    
    def test_start_miners(self):
        self.manager.start_miners(["foo"])
        self.manager.nodes["foo"].initialize.assert_called_once()
        self.manager.nodes["foo"].start_mining.assert_called_once()
        self.manager.nodes["bar"].initialize.assert_not_called()

    def test_stop_miners(self):
        self.manager.stop_miners(["foo"])
        self.manager.nodes["foo"].stop_mining.assert_called_once()
        self.manager.nodes["bar"].stop_mining.assert_not_called()

    def test_node_by_address(self):
        node = self.manager.node_by_address(make_dummy_address("foo"))
        self.assertEqual(node, self.manager.nodes["foo"])



class NodeContainerTest(unittest.TestCase):
    def setUp(self):
        self.container = NodeContainer()
    
    def test_add(self):
        self.assertEqual(len(self.container), 0)
        self.container.add(make_mock_node("foo"))
        self.assertEqual(len(self.container), 1)
    
    def test_get_item(self):
        self.container.add(make_mock_node("foo"))
        self.container.add(make_mock_node("bar"))
        self.assertEqual(self.container["foo"].name, "foo")
        self.assertEqual(self.container["bar"].name, "bar")
        self.assertEqual(self.container[0].name, "foo")
        self.assertEqual(self.container[1].name, self.container["bar"].name)
        with self.assertRaises(KeyError) as cm:
            self.container["baz"]
        self.assertEqual(str(cm.exception), "'baz'")

        with self.assertRaises(IndexError):
            self.container[2]

    def test_find(self):
        self.container.add(make_mock_node("foo"))
        self.container.add(make_mock_node("bar"))
        foo_addr = make_dummy_address("foo")
        self.assertEqual(self.container[0].address, foo_addr)
        self.assertEqual(self.container[0], self.container.find(lambda n: n.address == foo_addr))
        with self.assertRaises(ValueError):
            self.container.find(lambda n_: False)
