import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog
import os

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("300x150")
        
        # Username entry
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username = tk.Entry(self.root, width=30)
        self.username.pack(pady=5)
        
        # Login button
        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
        self.success = False
        self.username_value = None
        
    def login(self):
        if self.username.get().strip():
            self.username_value = self.username.get().strip()
            self.success = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Please enter a username")
            
    def mainloop(self):
        self.root.mainloop()
        return self.success, self.username_value

class ChatGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title(f"Secure Chat - {client.username}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame (users list)
        self.left_frame = tk.Frame(self.container, width=150)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(self.left_frame, text="Online Users").pack()
        self.users_listbox = tk.Listbox(self.left_frame, width=20, height=20)
        self.users_listbox.pack(fill=tk.Y, expand=True)
        
        # Right frame (chat)
        self.right_frame = tk.Frame(self.container)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(self.right_frame, text="Connected", fg="green")
        self.status_label.pack(pady=(0, 5))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.right_frame, wrap=tk.WORD, width=50, height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        self.input_frame = tk.Frame(self.right_frame)
        self.input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.message_input = tk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.upload_button = tk.Button(
            self.input_frame, text="📎", command=self.upload_file
        )
        self.upload_button.pack(side=tk.LEFT, padx=5)
        
        # Add history button
        self.history_button = tk.Button(
            self.input_frame,
            text="📜",
            command=self.show_history
        )
        self.history_button.pack(side=tk.LEFT, padx=5)
        
        self.send_button = tk.Button(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side=tk.LEFT)
        
        # Bind events
        self.message_input.bind('<Return>', lambda e: self.send_message())
        
        # Start checking messages
        self.check_messages()
    
    def update_users(self, users):
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)
    
    def send_message(self):
        message = self.message_input.get()
        if message:
            if self.client.send_message(message):
                self.message_input.delete(0, tk.END)
            else:
                self.show_error("Failed to send message")
    
    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                self.status_label.config(text="Sending file...", fg="blue")
                self.root.update()
                
                if self.client.send_file(filepath):
                    filename = os.path.basename(filepath)
                    self.status_label.config(text="File sent successfully", fg="green")
                    self.add_message("You", f"Sent file: {filename}")
                else:
                    self.show_error("Failed to send file")
                    self.status_label.config(text="Error sending file", fg="red")
            except Exception as e:
                self.show_error(f"Error sending file: {str(e)}")
                self.status_label.config(text="Error", fg="red")
            finally:
                # Reset status after 3 seconds
                self.root.after(3000, lambda: self.status_label.config(text="Connected", fg="green"))
    
    def show_error(self, message):
        self.status_label.config(text="Error", fg="red")
        messagebox.showerror("Error", message)
    
    def add_message(self, sender, message):
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.see(tk.END)
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Chat History")
        history_window.geometry("600x400")
        
        # Create history display
        history_display = scrolledtext.ScrolledText(
            history_window,
            wrap=tk.WORD,
            width=70,
            height=20
        )
        history_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Request history from server
        self.client.request_history()
        
        def update_history(messages):
            history_display.delete(1.0, tk.END)
            for msg in messages:
                sender, msg_type, content, timestamp, file_path = msg
                if msg_type == 'chat':
                    history_display.insert(tk.END, 
                        f"[{timestamp}] {sender}: {content}\n")
                elif msg_type == 'file':
                    history_display.insert(tk.END,
                        f"[{timestamp}] {sender} sent file: {content}\n")
        
        # Update history when received
        self.history_callback = update_history

    def check_messages(self):
        if not self.client.is_connected():
            self.status_label.config(text="Disconnected", fg="red")
            self.show_error("Connection lost")
            self.root.destroy()
            return
            
        messages = self.client.check_messages()
        for message in messages:
            if message['type'] == 'user_list':
                self.update_users(message['users'])
            elif message['type'] == 'chat':
                self.add_message(message['sender'], message['message'])
            elif message['type'] == 'file':
                self.handle_file_message(message)
            elif message['type'] == 'chat_history':
                if hasattr(self, 'history_callback'):
                    self.history_callback(message['history'])
        
        self.root.after(100, self.check_messages)
    
    def on_closing(self):
        self.client.close()
        self.root.destroy()
    
    def mainloop(self):
        self.root.mainloop() 