
# Secure Chat Application

A secure multi-user chat application built with Python, featuring real-time messaging, file sharing, and message history. The application uses SSL/TLS encryption for secure communication between clients and server.

## Features

- Secure encrypted communication
- Multi-user support
- Real-time messaging
- File sharing capabilities
- Message history
- User status updates
- Graphical User Interface


## Prerequisites

- Python 3.x
- pip (Python package installer)


## Setup & installation

1. Clone the repository:
```bash
git clone https://github.com/SharmisthaAlike/Secure-Blockchain-Based-Multi-User-Messaging-System
cd secure-chat
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Generate SSL certificate (if not present):
```bash
openssl req -x509 -newkey rsa:4096 -keyout app/certs/server.key -out app/certs/server.pem -days 365 -nodes -subj "/CN=localhost"
```


## Project Structure
```
app/
├── __init__.py
├── client.py        # Client-side implementation
├── server.py        # Server implementation
├── blockchain.py    # Blockchain implementation
├── gui.py           # User interface
├── crypto.py        # Cryptography handling
├── database.py      # Message storage
└── certs/           # SSL certificates
    └── server.pem
```

## Running the Application

### Starting the Server

1. On the server machine:
```bash
python -m app.server
```
2. Note the IP address displayed in the console

### Starting a Client

1. On the same machine (localhost):
```bash
python -m app.client
```

2. On a different machine (same network):
```bash
python -m app.client --server SERVER_IP
```
Replace `SERVER_IP` with the IP address shown by the server.

## Usage

1. Launch the client application
2. Enter your username in the login window
3. Start chatting!

### Features:
- Type messages in the input field and press Enter or click Send
- Click 📎 to send files
- Click 📜 to view message history
- See online users in the left panel
- Check connection status at the top


## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
