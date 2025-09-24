import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


class Database:
    def __init__(self, db_path: str = "data/psi.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # PSI sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS psi_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_size INTEGER,
                intersection_size INTEGER,
                intersection_data TEXT,
                client_ip TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Session tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        conn.commit()

        # Add role column to existing users table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        conn.close()

    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Validate role
        if role not in ["user", "admin"]:
            raise ValueError("Role must be 'user' or 'admin'")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> Optional[tuple]:
        """Verify user credentials and return (user_id, role)"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = cursor.fetchone()
        conn.close()

        return (result[0], result[1]) if result else None

    def create_session_token(self, user_id: int) -> str:
        """Create a new session token for user"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now().timestamp() + 24 * 60 * 60  # 24 hours

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO session_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires_at)
        )
        conn.commit()
        conn.close()

        return token

    def verify_session_token(self, token: str) -> Optional[tuple]:
        """Verify session token and return (user_id, role)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT st.user_id, u.role FROM session_tokens st
            JOIN users u ON st.user_id = u.id
            WHERE st.token = ? AND st.expires_at > ?
            """,
            (token, datetime.now().timestamp())
        )
        result = cursor.fetchone()
        conn.close()

        return (result[0], result[1]) if result else None

    def log_psi_session(
        self,
        user_id: int,
        client_size: int,
        intersection_size: int,
        intersection_data: List[str],
        client_ip: str,
        session_token: str = None
    ) -> int:
        """Log a PSI computation session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO psi_sessions
            (user_id, session_token, client_size, intersection_size, intersection_data, client_ip)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, session_token, client_size, intersection_size, json.dumps(intersection_data), client_ip)
        )

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return session_id

    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all PSI sessions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, client_size, intersection_size, client_ip
            FROM psi_sessions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            """,
            (user_id,)
        )

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "timestamp": row[1],
                "client_size": row[2],
                "intersection_size": row[3],
                "client_ip": row[4]
            })

        conn.close()
        return sessions

    def get_session_details(self, session_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, client_size, intersection_size, intersection_data, client_ip
            FROM psi_sessions
            WHERE id = ? AND user_id = ?
            """,
            (session_id, user_id)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "timestamp": row[1],
                "client_size": row[2],
                "intersection_size": row[3],
                "intersection_data": json.loads(row[4]) if row[4] else [],
                "client_ip": row[5]
            }

        return None

    def get_session_details_admin(self, session_id):
        """Get detailed information about any session (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.id, p.timestamp, p.client_size, p.intersection_size,
                   p.intersection_data, p.client_ip, u.username
            FROM psi_sessions p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
            """,
            (session_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "timestamp": row[1],
                "client_size": row[2],
                "intersection_size": row[3],
                "intersection_data": json.loads(row[4]) if row[4] else [],
                "client_ip": row[5],
                "username": row[6]
            }

        return None

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all PSI sessions (admin view)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.id, u.username, p.timestamp, p.client_size,
                   p.intersection_size, p.client_ip
            FROM psi_sessions p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.timestamp DESC
            """)

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "username": row[1],
                "timestamp": row[2],
                "client_size": row[3],
                "intersection_size": row[4],
                "client_ip": row[5]
            })

        conn.close()
        return sessions

    def get_all_sessions_with_data(self) -> List[Dict[str, Any]]:
        """Get all PSI sessions including intersection data (admin view)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.id, u.username, p.timestamp, p.client_size,
                   p.intersection_size, p.client_ip, p.intersection_data
            FROM psi_sessions p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.timestamp DESC
            """)

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "username": row[1],
                "timestamp": row[2],
                "client_size": row[3],
                "intersection_size": row[4],
                "client_ip": row[5],
                "intersection_data": json.loads(row[6]) if row[6] else []
            })

        conn.close()
        return sessions