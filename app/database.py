import sqlite3
from datetime import datetime
import json
import os

class ChatDatabase:
    def __init__(self):
        self.db_path = "app/chat_history.db"
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        os.makedirs("app", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    receiver TEXT DEFAULT 'all',
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT
                )
            ''')
            
            conn.commit()

    def save_message(self, sender, message_type, content, file_path=None, receiver="all"):
        """Save a message to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (sender, receiver, message_type, content, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender, receiver, message_type, content, file_path))
            conn.commit()

    def get_chat_history(self, limit=100):
        """Get recent chat history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, message_type, content, timestamp, file_path
                FROM messages
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

    def get_user_chat_history(self, username, limit=100):
        """Get chat history for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, message_type, content, timestamp, file_path
                FROM messages
                WHERE sender = ? OR receiver = ? OR receiver = 'all'
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (username, username, limit))
            return cursor.fetchall() 