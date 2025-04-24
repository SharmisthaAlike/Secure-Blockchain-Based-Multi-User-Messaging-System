import socket, ssl, threading
import json
import base64
import netifaces  # You might need to install this: pip install netifaces
from app.crypto import CryptoHandler
from app.database import ChatDatabase

def get_local_ips():
    ips = []
    for interface in netifaces.interfaces():
        try:
            # Get IPv4 address for each interface
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):  # Skip localhost
                        ips.append(ip)
        except:
            continue
    return ips

class SecureServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.clients = {}  # {connection: username}
        self.lock = threading.Lock()
        self.running = True
        self.db = ChatDatabase()
        self.setup_server()

    def setup_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile="app/certs/server.pem")

    def broadcast(self, message):
        data = (json.dumps(message) + '\n').encode()
        disconnected = []
        
        for client in self.clients:
            try:
                client.sendall(data)
            except:
                disconnected.append(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            self.remove_client(client)

    def remove_client(self, client):
        with self.lock:
            if client in self.clients:
                username = self.clients[client]
                del self.clients[client]
                try:
                    client.close()
                except:
                    pass
                
                # Notify others
                self.broadcast({
                    'type': 'chat',
                    'sender': 'Server',
                    'message': f"{username} left the chat"
                })
                self.broadcast({
                    'type': 'user_list',
                    'users': list(self.clients.values())
                })

    def handle_client(self, client_sock, addr):
        try:
            data = client_sock.recv(4096).decode()
            if not data:
                return
            
            message = json.loads(data.strip())
            if message['type'] == 'login':
                username = message['username']
                with self.lock:
                    self.clients[client_sock] = username
                    print(f"[+] New user connected: {username}")
                    # Announce new user
                    self.broadcast({
                        'type': 'chat',
                        'sender': 'Server',
                        'message': f"{username} joined the chat"
                    })
                    # Send updated user list
                    self.broadcast({
                        'type': 'user_list',
                        'users': list(self.clients.values())
                    })
                
                while True:
                    try:
                        data = client_sock.recv(4096).decode()
                        if not data:
                            break
                        
                        message = json.loads(data.strip())
                        if message['type'] == 'chat':
                            # Store chat message
                            self.db.save_message(
                                sender=username,
                                message_type='chat',
                                content=message['message']
                            )
                            # Broadcast message
                            self.broadcast({
                                'type': 'chat',
                                'sender': username,
                                'message': message['message']
                            })
                        elif message['type'] == 'file':
                            # Store file message
                            self.db.save_message(
                                sender=username,
                                message_type='file',
                                content=message['filename'],
                                file_path=f"downloads/{message['filename']}"
                            )
                            # Broadcast file
                            self.broadcast({
                                'type': 'file',
                                'sender': username,
                                'filename': message['filename'],
                                'file_data': message['file_data']
                            })
                        elif message['type'] == 'history_request':
                            # Handle history request
                            history = self.db.get_user_chat_history(username)
                            client_sock.send(json.dumps({
                                'type': 'chat_history',
                                'history': history
                            }).encode() + b'\n')
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error handling client message: {e}")
                        break
                        
        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            self.remove_client(client_sock)

    def start(self):
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            
            print("\n=== Server Information ===")
            print(f"Port: {self.port}")
            print("\nServer IP Addresses:")
            for ip in get_local_ips():
                print(f"  - {ip}")
            print("\nShare any of these IPs with clients on the same network")
            print("=========================\n")
            
            while self.running:
                try:
                    client_sock, addr = self.sock.accept()
                    ssl_sock = self.context.wrap_socket(client_sock, server_side=True)
                    print(f"[+] New connection from {addr}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(ssl_sock, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False
            self.sock.close()

if __name__ == "__main__":
    server = SecureServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.running = False