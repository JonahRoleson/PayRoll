import os
from cryptography.fernet import Fernet, InvalidToken

def _fernet() -> Fernet:
    key = os.getenv("DJANGO_FERNET_KEY")
    if not key:
        raise RuntimeError("DJANGO_FERNET_KEY is not set")
    return Fernet(key.encode())

def encrypt_str(value: str) -> str:
    if value is None:
        return ""
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt_str(token: str) -> str:
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        # Don’t leak details
        return ""
