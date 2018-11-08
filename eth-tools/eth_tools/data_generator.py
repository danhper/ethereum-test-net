from hypothesis import strategies


def char_range(first, last):
    return list(map(chr, range(ord(first), ord(last) + 1)))


def alphanum_chars():
    return char_range("a", "z") + char_range("A", "Z") + char_range("0", "9")


eth_strategies = {
    "address": strategies.text(alphabet=alphanum_chars(), min_size=40, max_size=40),
    "string": strategies.text(),
    "bytes": strategies.binary(),
    "byte32": strategies.binary(max_size=32),
    "uint256": strategies.integers(min_value=0, max_value=2 ** 256 - 1)
}


def type_to_strategy(type_string):
    is_list = type_string.endswith("[]")
    if is_list:
        type_string = type_string[:-2]
    strategy = eth_strategies[type_string]
    if is_list:
        strategy = strategies.lists(strategy)
    return strategy


def generate_example(type_string):
    return type_to_strategy(type_string).example()
