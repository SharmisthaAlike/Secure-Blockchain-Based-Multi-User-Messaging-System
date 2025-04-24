import socket, ssl
import json
import threading
import base64
import os
import argparse
from app.crypto import CryptoHandler
from app.gui import ChatGUI, LoginWindow

class SecureClient:
    def __init__(self, username, server_ip='127.0.0.1', port=9999):
        self.username = username
        self.server_ip = server_ip
        self.port = port
        self.running = True
        self.message_queue = []
        self.lock = threading.Lock()
        self.connected = False
        
        # Create downloads directory
        os.makedirs('downloads', exist_ok=True)
        
        # Connect to server
        if not self.connect():
            raise ConnectionError(f"Could not connect to server at {server_ip}:{port}")

    def connect(self):
        try:
            self.context = ssl.create_default_context()
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ssl_sock = self.context.wrap_socket(self.sock, server_hostname=self.server_ip)
            self.ssl_sock.connect((self.server_ip, self.port))
            
            # Send login info
            login_message = {
                'type': 'login',
                'username': self.username
            }
            self.send_message(login_message)
            
            self.connected = True
            
            # Start receiver thread
            self.receiver_thread = threading.Thread(target=self._receive_messages)
            self.receiver_thread.daemon = True
            self.receiver_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_message(self, message):
        try:
            if isinstance(message, str):
                message = {
                    'type': 'chat',
                    'message': message
                }
            data = json.dumps(message).encode() + b'\n'
            self.ssl_sock.sendall(data)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            return False

    def _receive_messages(self):
        buffer = ""
        while self.running and self.connected:
            try:
                chunk = self.ssl_sock.recv(4096)
                if not chunk:
                    break
                
                buffer += chunk.decode('utf-8')
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str:
                        try:
                            message = json.loads(message_str)
                            with self.lock:
                                self.message_queue.append(message)
                        except json.JSONDecodeError as e:
                            print(f"Invalid message format: {e}")
                
            except Exception as e:
                print(f"Receive error: {e}")
                break
        
        self.connected = False
        self.running = False

    def check_messages(self):
        with self.lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        return messages

    def is_connected(self):
        return self.connected

    def close(self):
        self.running = False
        self.connected = False
        try:
            self.ssl_sock.shutdown(socket.SHUT_RDWR)
            self.ssl_sock.close()
        except:
            pass

    def send_file(self, filepath):
        try:
            # Read file in binary mode
            with open(filepath, 'rb') as file:
                file_data = base64.b64encode(file.read()).decode('utf-8')
                filename = os.path.basename(filepath)
                
                # Create file message
                message = {
                    'type': 'file',
                    'filename': filename,
                    'file_data': file_data
                }
                
                # Send the message
                success = self.send_message(message)
                if success:
                    print(f"File sent: {filename}")
                return success
                
        except Exception as e:
            print(f"Error sending file: {e}")
            return False

    def save_file(self, filename, file_data):
        try:
            # Create downloads directory if it doesn't exist
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
            # Save file
            filepath = os.path.join('downloads', filename)
            with open(filepath, 'wb') as file:
                file_bytes = base64.b64decode(file_data)
                file.write(file_bytes)
            print(f"File saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

    def request_history(self):
        """Request chat history from server"""
        self.send_message({
            'type': 'history_request'
        })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Secure Chat Client')
    parser.add_argument('--server', '-s', 
                       default='127.0.0.1',
                       help='Server IP address to connect to')
    parser.add_argument('--port', '-p',
                       type=int,
                       default=9999,
                       help='Server port to connect to')
    
    args = parser.parse_args()
    
    try:
        print("\n=== Secure Chat Client ===")
        print(f"Attempting to connect to server at {args.server}:{args.port}")
        print("Please make sure the server is running first.")
        print("========================\n")
        
        login_window = LoginWindow()
        success, username = login_window.mainloop()
        
        if success:
            client = SecureClient(username, server_ip=args.server, port=args.port)
            chat_gui = ChatGUI(client)
            chat_gui.mainloop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'client' in locals():
            client.close()