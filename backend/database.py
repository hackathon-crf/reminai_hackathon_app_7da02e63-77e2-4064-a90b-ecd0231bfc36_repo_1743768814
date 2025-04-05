"""
Database module for the Questions Mentor backend.

This module handles all database operations including initialization,
user registration, and authentication. It uses SQLite as the database
engine and provides functions for managing user accounts with different roles.
"""

import sqlite3
from typing import Optional, Tuple, Union

def init_db() -> None:
    """
    Initialize the SQLite database and create the users table if it doesn't exist.

    The users table contains the following columns:
    - id: Unique identifier for each user (auto-incrementing)
    - username: Unique username for login
    - password: User's password (should be hashed in production)
    - role: User's role ('formateur', 'secouriste', or 'grand_public')
    - fullname: User's full name
    - email: User's email address
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,  -- "formateur", "secouriste", "grand_public"
        fullname TEXT,
        email TEXT
    )
    """)
    conn.commit()
    conn.close()

def register_user(username: str, password: str, role: str, fullname: str, email: str) -> bool:
    """
    Register a new user in the database.

    Args:
        username (str): Unique username for the new user
        password (str): User's password (should be hashed in production)
        role (str): User's role ('formateur', 'secouriste', or 'grand_public')
        fullname (str): User's full name
        email (str): User's email address

    Returns:
        bool: True if registration successful, False if username already exists

    Note:
        The function handles SQLite's IntegrityError for duplicate usernames
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role, fullname, email) VALUES (?, ?, ?, ?, ?)",
                       (username, password, role, fullname, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate a user and return their role.

    Args:
        username (str): The username to authenticate
        password (str): The password to verify

    Returns:
        Optional[str]: The user's role if authentication successful, None otherwise
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
