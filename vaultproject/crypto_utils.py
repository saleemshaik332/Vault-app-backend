"""
Encryption helpers for sensitive fields (ID numbers, bank details, vault passwords).

Uses Fernet (AES-128 in CBC mode with HMAC authentication) from the `cryptography`
library. The key is loaded from the ENCRYPTION_KEY environment variable so it is
never hard-coded or committed to source control.

IMPORTANT: If you lose the ENCRYPTION_KEY, all encrypted data becomes permanently
unreadable. Back it up somewhere safe (e.g. a password manager), separately from
the database itself.
"""
import os
from cryptography.fernet import Fernet, InvalidToken

_fernet = None


def get_fernet():
    global _fernet
    if _fernet is None:
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise RuntimeError(
                "ENCRYPTION_KEY is not set. Generate one with: "
                "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
                "and put it in your .env file."
            )
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string, returning a token safe to store as text in a DB column."""
    if plaintext is None:
        return ""
    f = get_fernet()
    return f.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_value(token: str) -> str:
    """Decrypt a token produced by encrypt_value. Returns '' if empty/invalid."""
    if not token:
        return ""
    f = get_fernet()
    try:
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return "[unable to decrypt]"


def mask_value(plaintext_len_hint: str, visible_chars: int = 4) -> str:
    """Return a masked preview like '••••••1234' for display in list views."""
    if not plaintext_len_hint:
        return ""
    tail = plaintext_len_hint[-visible_chars:] if len(plaintext_len_hint) > visible_chars else plaintext_len_hint
    return "•" * max(len(plaintext_len_hint) - len(tail), 4) + tail
