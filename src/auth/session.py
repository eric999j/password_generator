"""
Session 管理器
負責管理加密的認證狀態
"""

import secrets
from src.crypto.encryption import encrypt, decrypt

class SessionManager:
    """管理加密的記憶體認證狀態"""
    
    _instance = None
    _session_token = None
    _secret_check = secrets.token_hex(16)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_authenticated(self):
        """加密存入認證成功狀態"""
        self._session_token = encrypt(self._secret_check)
        
    def is_authenticated(self) -> bool:
        """驗證認證狀態"""
        if not self._session_token:
            return False
        try:
            decrypted = decrypt(self._session_token)
            return decrypted == self._secret_check
        except Exception:
            return False

# 全局單例
session = SessionManager()
