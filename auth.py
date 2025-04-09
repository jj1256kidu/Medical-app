import streamlit as st
import bcrypt
from datetime import datetime, timedelta
import jwt
import json
import os
from typing import Dict, Optional

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthHandler:
    def __init__(self):
        self.users_file = "users.json"
        self.load_users()

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                self.users = json.load(f)
        else:
            self.users = {
                "doctor": {
                    "password": self.hash_password("doctor123"),
                    "role": "Doctor",
                    "name": "Dr. Smith",
                    "email": "doctor@hospital.com",
                    "last_login": None
                },
                "nurse": {
                    "password": self.hash_password("nurse123"),
                    "role": "Nurse",
                    "name": "Nurse Johnson",
                    "email": "nurse@hospital.com",
                    "last_login": None
                },
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "Admin",
                    "name": "Admin",
                    "email": "admin@hospital.com",
                    "last_login": None
                }
            }
            self.save_users()

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f)

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def create_access_token(self, data: Dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.JWTError:
            return None

    def login(self, username: str, password: str) -> Optional[Dict]:
        if username in self.users and self.verify_password(password, self.users[username]["password"]):
            user_data = self.users[username].copy()
            user_data.pop("password")
            user_data["username"] = username
            user_data["last_login"] = datetime.now().isoformat()
            self.users[username]["last_login"] = user_data["last_login"]
            self.save_users()
            return user_data
        return None

    def register_user(self, username: str, password: str, role: str, name: str, email: str) -> bool:
        if username in self.users:
            return False
        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "name": name,
            "email": email,
            "last_login": None
        }
        self.save_users()
        return True

    def update_user(self, username: str, **kwargs) -> bool:
        if username not in self.users:
            return False
        for key, value in kwargs.items():
            if key != "password" and key in self.users[username]:
                self.users[username][key] = value
        self.save_users()
        return True

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        if username in self.users and self.verify_password(old_password, self.users[username]["password"]):
            self.users[username]["password"] = self.hash_password(new_password)
            self.save_users()
            return True
        return False

    def delete_user(self, username: str) -> bool:
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True
        return False 
