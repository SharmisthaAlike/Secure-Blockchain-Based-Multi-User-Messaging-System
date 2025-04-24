import json
from web3 import Web3
import hashlib
import os

class BlockchainManager:
    def __init__(self):
        with open(os.path.join("app/contracts/deploy_config.json")) as f:
            data = json.load(f)
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        self.contract = self.w3.eth.contract(
            address=data["address"],
            abi=data["abi"]
        )
        self.account = data["account"]

    def store_hash(self, message):
        h = hashlib.sha256(message.encode()).hexdigest()
        tx = self.contract.functions.storeHash(h).transact({"from": self.account})
        return tx

    def verify_hash(self, message):
        h = hashlib.sha256(message.encode()).hexdigest()
        return self.contract.functions.verifyHash(h).call()
