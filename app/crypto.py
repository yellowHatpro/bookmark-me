import json
from typing import Any

from cryptography.fernet import Fernet

from app.config import get_settings


def _fernet() -> Fernet:
    key = get_settings().app_fernet_key
    if not key:
        raise RuntimeError(
            "APP_FERNET_KEY is not set. Generate one with "
            "`python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'` "
            "and put it in .env."
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_json(payload: dict[str, Any]) -> bytes:
    return _fernet().encrypt(json.dumps(payload).encode())


def decrypt_json(blob: bytes) -> dict[str, Any]:
    return json.loads(_fernet().decrypt(blob).decode())


def generate_key() -> str:
    return Fernet.generate_key().decode()
