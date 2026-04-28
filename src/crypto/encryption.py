"""
加密/解密模組
使用 cryptography.fernet 提供對稱加密
"""

from cryptography.fernet import Fernet
from src.config import Config
from .platform_security import protect_key, unprotect_key


class _EncryptionManager:
    """加密管理器 (單例)"""
    
    _instance = None
    _cipher = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cipher()
        return cls._instance
    
    def _init_cipher(self):
        """初始化或載入加密 cipher"""
        Config.ensure_dirs()
        
        if Config.KEY_FILE.exists():
            # 載入並使用平台安全機制解密金鑰
            protected_key = Config.KEY_FILE.read_bytes()
            try:
                key = unprotect_key(protected_key)
            except Exception as e:
                # 關鍵修復：如果解密失敗，絕不自動生成新金鑰，避免舊資料永久丟失
                raise RuntimeError(
                    f"無法解密金鑰：{e}\n"
                    "這可能是因為系統認證環境已變更或金鑰檔損毀。\n"
                    "為了防止資料庫中的現有密碼永久丟失，程式將終止啟動。"
                ) from e
        else:
            # 只有在完全沒有金鑰檔的情況下（初次啟動）才生成新金鑰
            key = Fernet.generate_key()
            Config.KEY_FILE.write_bytes(protect_key(key))
        
        self._cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """加密文本"""
        return self._cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """解密文本"""
        return self._cipher.decrypt(ciphertext.encode()).decode()


# 模組級便捷函數
def encrypt(text: str) -> str:
    """加密文本"""
    return _EncryptionManager().encrypt(text)


def decrypt(text: str) -> str:
    """解密文本"""
    return _EncryptionManager().decrypt(text)
