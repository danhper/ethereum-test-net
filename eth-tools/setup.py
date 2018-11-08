from setuptools import setup, find_packages


setup(
    name="eth_tools",
    version="0.1.0",
    packages=find_packages(),
    scripts=["./bin/eth-tools"],
    install_requires=[
        "web3",
        "filelock",
    ]
)
