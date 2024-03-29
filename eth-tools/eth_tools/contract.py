from functools import lru_cache
import json
import subprocess
from typing import Optional, List, Any

from .data_generator import DataGenerator


class Contract:
    def __init__(self, name: str, abi: dict, bytecode: Optional[str],
                 address: Optional[str] = None):
        self.name = name
        self.abi = abi
        self.address = address
        self.bytecode = bytecode

    @property
    @lru_cache()
    def constructor_abi(self):
        for entity in self.abi:
            if entity.get("type") == "constructor":
                return entity
        return None

    def __repr__(self):
        return "Contract(name='{0}')".format(self.name)

    @lru_cache()
    def get_function_abi(self, name: str, raise_on_multiple=False):
        candidates = [f for f in self.abi if f["type"] == "function" and f.get("name") == name]
        if not candidates:
            raise ValueError("no function named {0}".format(name))
        if len(candidates) > 1 and raise_on_multiple:
            raise ValueError("multiple functions named {0}".format(name))
        return candidates[0]

    @property
    def function_names(self):
        return [func["name"] for func in self.abi if func.get("type") == "function"]

    @classmethod
    def _find_top_level_contract(cls, spec):
        blacklisted = set()
        candidates = {}
        contracts = [contract for source in spec["sources"].values()
                              for contract in source["AST"]["children"]
                              if contract["attributes"].get("contractKind") == "contract"]

        for contract in contracts:
            if not contract["id"] in blacklisted:
                candidates[contract["id"]] = contract["attributes"]["name"]
            for dependency in contract["attributes"].get("contractDependencies", []):
                if dependency:
                    blacklisted.add(dependency)
                candidates.pop(dependency, None)

        if not candidates:
            raise ValueError("no top level contract found")
        elif len(candidates) > 1:
            raise ValueError("multiple to level contracts found")
        else:
            name = list(candidates.values())[0]
            return name, cls._find_contract_by_name(spec["contracts"], name)

    @staticmethod
    def _find_contract_by_name(contracts, contract_name):
        for key, value in contracts.items():
            name = key.split(":")[1]
            if contract_name == name:
                return value
        raise ValueError("contract {0} not found".format(contract_name))

    @classmethod
    def _find_contract(cls, spec, name: Optional[str] = None):
        if name:
            return name, cls._find_contract_by_name(spec["contracts"], name)
        return cls._find_top_level_contract(spec)

    @classmethod
    def from_full_spec(cls, full_spec: dict, contract_name: Optional[str] = None,
                       address: Optional[str] = None):
        name, contract_data = cls._find_contract(full_spec, contract_name)
        abi = json.loads(contract_data["abi"])
        bytecode = contract_data["bin"]
        return cls(name=name, abi=abi, bytecode=bytecode)

    @classmethod
    def from_json_file(cls, filepath: str, contract_name: Optional[str] = None,
                       address: Optional[str] = None):
        """the JSON file should be generated by the following command
        solc contract.sol --combined-json abi,bin,ast

        If multiple independant contracts are generated, the contract_name must
        be passed explicitly
        """
        with open(filepath) as f:
            full_spec = json.load(f)
        return cls.from_full_spec(full_spec, contract_name=contract_name, address=address)

    @classmethod
    def from_sol_file(cls, filepath: str, contract_name: Optional[str] = None,
                      address: Optional[str] = None):
        proc = subprocess.Popen(
            ["solc", filepath, "--combined-json", "abi,bin,ast"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise ValueError("solc compilation failed with code {0}: "
                             "{1}".format(proc.returncode, stderr.decode("utf-8")))
        return cls.from_full_spec(json.loads(stdout), contract_name=contract_name, address=address)

    @classmethod
    def from_file(cls, filepath: str, contract_name: Optional[str] = None,
                  address: Optional[str] = None):
        if filepath.endswith(".json"):
            return cls.from_json_file(filepath, contract_name=contract_name, address=address)
        elif filepath.endswith(".sol"):
            return cls.from_sol_file(filepath, contract_name=contract_name, address=address)
        else:
            raise ValueError("unknown file type for {0}".format(filepath))
