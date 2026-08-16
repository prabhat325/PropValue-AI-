"""
Full-Stack Authentication and Cloud Persistence Module for PropValue AI.
Includes SQLite database management, PBKDF2-SHA256 password hashing,
and HMAC-SHA256 JWT token issuance and verification.
"""

import os
import sqlite3
import hashlib
import hmac
import base64
import json
import time
import secrets
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Header, Depends

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")
JWT_SECRET = os.environ.get("PROPVALUE_JWT_SECRET", "propvalue_ai_super_secret_jwt_key_2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 60 * 60 * 24 * 7  # 7 days

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Licensed Appraiser',
            license_number TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_valuations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            property_data TEXT NOT NULL,
            predicted_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Seed demo account if not exists
    cursor.execute("SELECT id FROM users WHERE email = ?", ("prabhat@propvalue.ai",))
    if not cursor.fetchone():
        salt = secrets.token_hex(16)
        pwd_hash = hash_password("password123", salt)
        cursor.execute("""
            INSERT INTO users (email, full_name, password_hash, salt, role, license_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("prabhat@propvalue.ai", "Prabhat Dubey", pwd_hash, salt, "Lead Valuation Analyst & Appraiser", "CA-BRE# 02948102"))
        conn.commit()

    conn.close()

# Password Hashing with PBKDF2-SHA256 (100,000 iterations)
def hash_password(password: str, salt: str) -> str:
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex()

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    actual_hash = hash_password(password, salt)
    return hmac.compare_digest(actual_hash, expected_hash)

# Base64URL Helpers
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64url_decode(s: str) -> bytes:
    padding = '=' * (4 - (len(s) % 4)) if len(s) % 4 != 0 else ''
    return base64.urlsafe_b64decode((s + padding).encode('utf-8'))

# JWT Token Creation & Verification
def create_jwt_token(payload: Dict[str, Any]) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload_copy = payload.copy()
    payload_copy["exp"] = int(time.time()) + JWT_EXPIRATION_SECONDS
    payload_copy["iat"] = int(time.time())

    header_b64 = _b64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _b64url_encode(json.dumps(payload_copy).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')

    signature = hmac.new(JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_jwt_token(token: str) -> Dict[str, Any]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise HTTPException(status_code=401, detail="Invalid token signature")

        payload = json.loads(_b64url_decode(payload_b64).decode('utf-8'))
        if payload.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

# FastAPI Dependency for Authenticated User
def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Malformed token payload")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, role, license_number, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="User account not found")

    return dict(row)

# Initialize DB on module import
init_db()
