"""
集中配置模組
統一管理路徑、常數等設定
"""

from pathlib import Path
import platform
import getpass
import json


class Config:
    """應用程式配置"""

    _SYSTEM = platform.system()

    # 作業系統偵測
    IS_WINDOWS = _SYSTEM == 'Windows'
    IS_MAC = _SYSTEM == 'Darwin'
    IS_LINUX = _SYSTEM == 'Linux'

    # 應用名稱
    APP_NAME = '強密碼產生器'

    # 數據目錄
    if IS_WINDOWS:
        APP_DATA_DIR = Path.home() / 'AppData' / 'Local' / '.password_generator'
    else:
        # Mac/Linux 使用標準隱藏目錄
        APP_DATA_DIR = Path.home() / '.password_generator'

    # 檔案路徑
    KEY_FILE = APP_DATA_DIR / 'key.key'
    DB_FILE = APP_DATA_DIR / 'passwords.db'
    SETTINGS_FILE = APP_DATA_DIR / 'settings.json'

    # 密碼強度配置
    STRENGTH_LEVELS = {
        '低': {'length': 8, 'use_special': False},
        '中': {'length': 10, 'use_special': True},
        '高': {'length': 12, 'use_special': True},
    }

    # 強度評分閾值
    STRENGTH_WEAK_THRESHOLD = 33
    STRENGTH_MEDIUM_THRESHOLD = 66

    # GUI 配置
    WINDOW_SIZE = '600x700'
    THEME = 'darkly'

    @classmethod
    def get_current_user(cls) -> str:
        """取得當前系統用戶名"""
        return getpass.getuser()

    @classmethod
    def ensure_dirs(cls):
        """確保必要的目錄存在"""
        cls.APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_theme(cls) -> str:
        """從設定檔讀取主題"""
        cls.ensure_dirs()
        if not cls.SETTINGS_FILE.exists():
            return cls.THEME

        try:
            with cls.SETTINGS_FILE.open('r', encoding='utf-8') as f:
                settings = json.load(f)
        except (OSError, json.JSONDecodeError):
            return cls.THEME

        theme = settings.get('theme', cls.THEME)
        return theme if isinstance(theme, str) and theme else cls.THEME

    @classmethod
    def save_theme(cls, theme_name: str):
        """保存主題設定"""
        cls.ensure_dirs()
        settings = {}
        if cls.SETTINGS_FILE.exists():
            try:
                with cls.SETTINGS_FILE.open('r', encoding='utf-8') as f:
                    settings = json.load(f)
            except (OSError, json.JSONDecodeError):
                settings = {}

        settings['theme'] = theme_name
        with cls.SETTINGS_FILE.open('w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
