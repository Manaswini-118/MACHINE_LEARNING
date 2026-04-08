# users.py - User management system
import hashlib
import json
import os

USER_DB_FILE = 'users.json'

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_db():
    """Initialize user database"""
    if not os.path.exists(USER_DB_FILE):
        users = {
            "doctor": {
                "password": hash_password("doctor123"),
                "role": "doctor",
                "name": "Dr. Sarah Johnson",
                "specialty": "Cardiologist",
                "email": "dr.sarah@heartguardian.com"
            },
            "patient": {
                "password": hash_password("patient123"),
                "role": "patient",
                "name": "John Anderson",
                "age": 45,
                "medical_history": "Hypertension",
                "email": "john.anderson@email.com"
            }
        }
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    return load_users()

def load_users():
    """Load users from file"""
    with open(USER_DB_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Save users to file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def verify_user(username, password):
    """Verify user credentials"""
    users = load_users()
    if username in users:
        if users[username]["password"] == hash_password(password):
            return users[username]
    return None

def register_user(username, password, name, email, role="patient", **kwargs):
    """Register new user"""
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": hash_password(password),
        "role": role,
        "name": name,
        "email": email,
        **kwargs
    }
    save_users(users)
    return True, "Registration successful"

# Initialize database
init_user_db()