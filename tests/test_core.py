import pytest
import os
import sys
from pathlib import Path

# 自動將專案根目錄加入 Python 路徑，解決 ModuleNotFoundError
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.password_generator import PasswordGenerator
from src.crypto.encryption import encrypt, decrypt
from src.auth.session import session

def test_password_generator_length():
    """測試生成的密碼長度"""
    pwd_low = PasswordGenerator.generate('低')
    pwd_med = PasswordGenerator.generate('中')
    pwd_high = PasswordGenerator.generate('高')
    
    assert len(pwd_low) == 8
    assert len(pwd_med) == 10
    assert len(pwd_high) == 12

def test_password_evaluation():
    """測試強度評估邏輯"""
    # 弱密碼
    score1, _, level1 = PasswordGenerator.evaluate("123")
    assert level1 == "弱"
    
    # 強密碼
    score2, _, level2 = PasswordGenerator.evaluate("P@ssw0rd2025!#")
    assert level2 == "強"
    assert score2 > 80

def test_encryption_decryption():
    """測試加密與解密一致性"""
    original = "Secret_123_Test"
    encrypted = encrypt(original)
    assert encrypted != original
    
    decrypted = decrypt(encrypted)
    assert decrypted == original

def test_session_auth_state():
    """測試認證狀態管理"""
    assert session.is_authenticated() is False
    session.set_authenticated()
    assert session.is_authenticated() is True
