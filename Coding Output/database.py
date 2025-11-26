"""
database module
handles all database operations
uses singleton pattern - only one connection allowed
"""

import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    """singleton - only one instance exists."""
    
    # stores single instance
    _instance = None 
    # tracks initialization 
    _initialized = False  
    
    def __new__(cls):
        """singleton , ensure only one instance."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path="music_copyright.db"):
        """initialize database connection."""
        # only initialize once
        if not DatabaseManager._initialized:
            self.db_path = db_path
            # connectting to sqlite
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            # return rows as dictionaries
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            # creating tables
            self._create_tables()
            DatabaseManager._initialized = True
    
    def _create_tables(self):
        """create database tables."""
        # creating users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # creating artefacts table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS artefacts (
                artefact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                artefact_name TEXT NOT NULL,
                artefact_type TEXT NOT NULL CHECK(artefact_type IN ('lyrics', 'score', 'audio')),
                file_path TEXT NOT NULL,
                encrypted_data BLOB NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                modified_at TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            )
        """)
        
        # creating indexes for faster queries
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_owner_id ON artefacts(owner_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_artefact_type ON artefacts(artefact_type)
        """)
        
        # saving changes
        self.connection.commit()
    
    def create_user(self, username, password_hash, role):
        """adding new user to database."""
        try:
            self.cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            self.connection.commit()
            # return new user id
            return self.cursor.lastrowid  
        except sqlite3.IntegrityError:
            raise ValueError("username already exists")
    
    def get_user(self, username):
        """get user by username."""
        self.cursor.execute("""
            SELECT * FROM users WHERE username = ?
        """, (username,))
        row = self.cursor.fetchone()
        if row:
             # converting to dict
            return dict(row) 
        return None
    
    def get_user_by_id(self, user_id):
        """getting user by id."""
        self.cursor.execute("""
            SELECT * FROM users WHERE user_id = ?
        """, (user_id,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def create_artefact(self, owner_id, artefact_name, artefact_type, file_path, encrypted_data, checksum):
        """adding new artefact to database."""
        created_at = datetime.now().isoformat()  
        self.cursor.execute("""
            INSERT INTO artefacts 
            (owner_id, artefact_name, artefact_type, file_path, 
             encrypted_data, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (owner_id, artefact_name, artefact_type, file_path, 
              encrypted_data, checksum, created_at))
        self.connection.commit()
        return self.cursor.lastrowid  
    
    def get_artefact(self, artefact_id):
        """getting artefact by id."""
        self.cursor.execute("""
            SELECT * FROM artefacts WHERE artefact_id = ?
        """, (artefact_id,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_user_artefacts(self, user_id):
        """getting all artefacts for a user."""
        self.cursor.execute("""
            SELECT artefact_id, artefact_name, artefact_type, 
                   created_at, modified_at, checksum
            FROM artefacts WHERE owner_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = self.cursor.fetchall()
        # converting rows to dictionaries
        result = []
        for row in rows:
            result.append(dict(row))
        return result
    
    def get_all_artefacts(self):
        """getting all artefacts (admin only)."""
        self.cursor.execute("""
            SELECT a.artefact_id, a.artefact_name, a.artefact_type,
                   a.created_at, a.modified_at, a.checksum,
                   u.username as owner_username
            FROM artefacts a
            JOIN users u ON a.owner_id = u.user_id
            ORDER BY a.created_at DESC
        """)
        rows = self.cursor.fetchall()
        # converting to list of dicts
        result = []
        for row in rows:
            result.append(dict(row))
        return result
    
    def update_artefact(self, artefact_id, encrypted_data, checksum):
        """update artefact data."""
         # updating timestamp
        modified_at = datetime.now().isoformat() 
        self.cursor.execute("""
            UPDATE artefacts 
            SET encrypted_data = ?, checksum = ?, modified_at = ?
            WHERE artefact_id = ?
        """, (encrypted_data, checksum, modified_at, artefact_id))
        self.connection.commit()
        # true if updated
        return self.cursor.rowcount > 0  
    
    def delete_artefact(self, artefact_id):
        """delete artefact."""
        self.cursor.execute("""
            DELETE FROM artefacts WHERE artefact_id = ?
        """, (artefact_id,))
        self.connection.commit()
        # true if deleted
        return self.cursor.rowcount > 0  
    
    def delete_user(self, user_id):
        """delete user and all their artefacts."""
        # deleting user's artefacts first
        self.cursor.execute("""
            DELETE FROM artefacts WHERE owner_id = ?
        """, (user_id,))
        
        # deleting user
        self.cursor.execute("""
            DELETE FROM users WHERE user_id = ?
        """, (user_id,))
        
        self.connection.commit()
        # true if deleted
        return self.cursor.rowcount > 0  
    
    def close(self):
        """closing database connection."""
        if self.connection:
            self.connection.close()
            DatabaseManager._initialized = False

