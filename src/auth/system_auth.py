"""
跨平台系統認證模組
支援 Windows (LogonUser), Mac/Linux (PAM)
"""

import platform
import getpass
from tkinter import simpledialog, messagebox
import tkinter as tk

from src.config import Config
from .session import session

def _verify_windows(username: str, password: str) -> bool:
    """Windows 認證實作"""
    import ctypes
    from ctypes.wintypes import HANDLE, LPCWSTR, DWORD
    
    LOGON32_LOGON_INTERACTIVE = 2
    LOGON32_PROVIDER_DEFAULT = 0
    
    try:
        advapi32 = ctypes.windll.advapi32
        kernel32 = ctypes.windll.kernel32
        
        # 處理 Domain\User 格式
        domain = None
        if '\\' in username:
            domain, username = username.split('\\', 1)
            
        handle = HANDLE()
        result = advapi32.LogonUserW(
            LPCWSTR(username),
            LPCWSTR(domain),
            LPCWSTR(password),
            DWORD(LOGON32_LOGON_INTERACTIVE),
            DWORD(LOGON32_PROVIDER_DEFAULT),
            ctypes.byref(handle)
        )
        if result:
            kernel32.CloseHandle(handle)
            return True
        return False
    except Exception:
        return False

def _verify_unix(username: str, password: str) -> bool:
    """Mac/Linux PAM 認證實作"""
    try:
        import pamela
        return pamela.authenticate(username, password)
    except ImportError:
        # 如果沒有安裝 pamela，嘗試使用簡單的系統檢查 (僅供開發參考)
        return False
    except Exception:
        return False

def verify_credentials(username: str, password: str) -> bool:
    """統一認證入口"""
    if Config.IS_WINDOWS:
        return _verify_windows(username, password)
    else:
        return _verify_unix(username, password)

def authenticate_user() -> bool:
    """交互式認證當前用戶"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # 取得當前系統用戶名
    current_user = Config.get_current_user()
    
    password = simpledialog.askstring(
        "系統認證",
        f"請輸入系統用戶 {current_user} 的密碼:",
        show='*'
    )
    
    root.destroy()
    
    if password is None:
        return False
    
    if verify_credentials(current_user, password):
        session.set_authenticated()
        messagebox.showinfo("認證成功", "認證成功，應用程式將啟動。")
        return True
    else:
        messagebox.showerror("認證失敗", "密碼不正確，應用程式將退出。")
        return False
