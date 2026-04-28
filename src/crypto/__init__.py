"""加密模組"""
from .encryption import encrypt, decrypt
from .secure_string import SecureString
from .platform_security import protect_key, unprotect_key

__all__ = ['encrypt', 'decrypt', 'SecureString', 'protect_key', 'unprotect_key']
