
# Secure-Blockchain-Based-Multi-User-Messaging-System

This project implements a secure, decentralized messaging system that uses AES encryption, Ethereum blockchain verification, and IPFS storage to ensure message integrity and privacy. The system supports multi-user communication, RSA-based authentication, and message acknowledgments, making it a trustless and tamper-proof chat platform. The system is now optimized for deployment on Railway.app using FastAPI as the backend.


## Features

- End-to-End Encrypted Messaging (AES-256)
- User Authentication with RSA Keys (Public-Private Key Encryption)
- Blockchain-Based Message Verification (Ethereum & Web3.py)
- Multi-User Support (WebSockets-based real-time chat via FastAPI)
- Decentralized Message Storage (IPFS Integration)
- Message Delivery Acknowledgments
- Timestamped Messages
- Deployed on Railway.app using Python (FastAPI)


## Tech Stack

Python (FastAPI, Web3.py, Cryptography, WebSockets)

Solidity (Ethereum Smart Contract for message verification)

IPFS (Decentralized message storage)

Ganache (Ethereum Local Testnet)

Railway.app (Serverless deployment)
## Setup & installation

Install Dependencies
```bash
pip install fastapi uvicorn web3 cryptography pycryptodome ipfshttpclient
```

Generate RSA Keys for Authentication
```python
from Crypto.PublicKey import RSA

def generate_keys():
    key = RSA.generate(2048)
    with open("private_key.pem", "wb") as f:
        f.write(key.export_key())
    with open("public_key.pem", "wb") as f:
        f.write(key.publickey().export_key())
    print("RSA Key Pair Generated!")

generate_keys()
```

Run the FastAPI WebSocket Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Run the Chat Client
```bash
  python client.py
```


## Deploying on Railway.app

1. Install Railway CLI:
```bash
curl -fsSL https://railway.app/install.sh | sh
```

2. Login to railway:
```bash
railway login
```

3. Initialize Railway project:
```bash
railway init
```

4. Deploy FastAPI server:
```bash
railway up
```
## Ethereum Smart Contract Deployment
1. Use Remix IDE or Hardhat to deploy SecureMessaging.sol.
2. Copy the deployed contract address and update contract_address in Python scripts.
3. Start Ganache and connect Web3.py to http://127.0.0.1:8545.
## License

[MIT](https://choosealicense.com/licenses/mit/)