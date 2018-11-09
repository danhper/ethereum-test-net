from cachetools.func import ttl_cache

from hypothesis import strategies


def char_range(first, last):
    return list(map(chr, range(ord(first), ord(last) + 1)))


def alphanum_chars():
    return char_range("a", "z") + char_range("A", "Z") + char_range("0", "9")


class DataGenerator:
    STATIC_STRATEGIES = {
        "string": strategies.text(),
        "bytes": strategies.binary(),
        "byte32": strategies.binary(max_size=32),
        "uint256": strategies.integers(min_value=0, max_value=2 ** 256 - 1)
    }

    def __init__(self, node):
        self._node = node

    def get_strategy(self, name):
        is_list = name.endswith("[]")
        if is_list:
            name = name[:-2]
        strategy = self.STATIC_STRATEGIES.get(name, getattr(self, name, None))
        if not strategy:
            raise ValueError("unknown type {0}".format(name))
        if is_list:
            strategy = strategies.lists(strategy, unique=True)
        return strategy

    def generate_example(self, name):
        return self.get_strategy(name).example()

    @property
    @ttl_cache()
    def address(self):
        addresses = list(self._node.list_all_accounts())
        return strategies.sampled_from(addresses)
