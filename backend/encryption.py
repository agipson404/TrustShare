# encryption.py

from cryptography.fernet import Fernet
import hashlib, base64

def get_user_key(username: str) -> bytes:
    # For demo, we derive a key from username and a secret salt
    salt = "mysupersecret_salt"
    key = hashlib.sha256((username + salt).encode()).digest()
    return base64.urlsafe_b64encode(key)

def get_fernet(username: str) -> Fernet:
    return Fernet(get_user_key(username))
