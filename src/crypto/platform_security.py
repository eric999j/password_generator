"""
跨平台安全儲存模組
Windows: DPAPI
Mac/Linux: Keyring (Keychain / Secret Service)
"""

import platform
from src.config import Config

def protect_key(key: bytes) -> bytes:
    """加密保護金鑰"""
    if Config.IS_WINDOWS:
        import ctypes
        from ctypes import wintypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
        
        data_in = DATA_BLOB(len(key), ctypes.cast(ctypes.create_string_buffer(key), ctypes.POINTER(ctypes.c_char)))
        data_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptProtectData(ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)):
            result = ctypes.string_at(data_out.pbData, data_out.cbData)
            ctypes.windll.kernel32.LocalFree(data_out.pbData)
            return result
        raise Exception("DPAPI 加密失敗")
    else:
        # Mac/Linux: 使用 keyring 儲存金鑰，檔案中只存一個標記
        import keyring
        import base64
        key_b64 = base64.b64encode(key).decode()
        keyring.set_password(Config.APP_NAME, "master_key", key_b64)
        return b"KEY_STORED_IN_KEYRING"

def unprotect_key(protected_data: bytes) -> bytes:
    """解密保護的金鑰"""
    if Config.IS_WINDOWS:
        import ctypes
        from ctypes import wintypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
            
        data_in = DATA_BLOB(len(protected_data), ctypes.cast(ctypes.create_string_buffer(protected_data), ctypes.POINTER(ctypes.c_char)))
        data_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)):
            result = ctypes.string_at(data_out.pbData, data_out.cbData)
            ctypes.windll.kernel32.LocalFree(data_out.pbData)
            return result
        raise Exception("DPAPI 解密失敗")
    else:
        # Mac/Linux: 從 keyring 讀取
        import keyring
        import base64
        key_b64 = keyring.get_password(Config.APP_NAME, "master_key")
        if key_b64:
            return base64.b64decode(key_b64)
        raise Exception("無法從系統金鑰環取得金鑰")
