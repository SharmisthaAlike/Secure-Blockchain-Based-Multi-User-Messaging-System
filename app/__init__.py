import os
import subprocess
import json
from solcx import compile_standard, install_solc
from web3 import Web3

def generate_ssl_cert():
    os.makedirs("app/certs", exist_ok=True)
    if not os.path.exists("app/certs/server.pem"):
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", "app/certs/server.pem",
            "-out", "app/certs/server.pem",
            "-days", "365",
            "-nodes", "-subj", "/CN=localhost"
        ])
        print("[+] SSL certificate generated.")

def deploy_contract():
    install_solc('0.8.0')
    with open("app/contracts/MessageStore.sol", "r") as file:
        source_code = file.read()

    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            "MessageStore.sol": {
                "content": source_code
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode"]
                }
            }
        }
    })

    with open("app/contracts/MessageStore.json", "w") as f:
        json.dump(compiled, f)

    bytecode = compiled["contracts"]["MessageStore.sol"]["MessageStore"]["evm"]["bytecode"]["object"]
    abi = compiled["contracts"]["MessageStore.sol"]["MessageStore"]["abi"]

    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    w3.eth.default_account = w3.eth.accounts[0]

    MessageStore = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = MessageStore.constructor().transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    address = tx_receipt.contractAddress

    with open("app/contracts/deploy_config.json", "w") as f:
        json.dump({
            "abi": abi,
            "address": address,
            "account": w3.eth.default_account
        }, f)

    print(f"[+] Contract deployed at: {address}")

if __name__ == "__main__":
    generate_ssl_cert()
    deploy_contract()
    print("\n🎉 Project initialized. You're ready to launch the app!")
