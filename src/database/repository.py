"""
密碼資料存取層
使用 SQLite + Context Manager
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict
import queue

from src.config import Config
from src.crypto import encrypt, decrypt
from src.auth.session import session


class SQLitePool:
    """簡單的 SQLite 連線池"""
    def __init__(self, db_path: str, size: int = 5):
        self.db_path = db_path
        self.size = size
        self.pool = queue.Queue(maxsize=size)
        for _ in range(size):
            conn = sqlite3.connect(db_path, check_same_thread=False, timeout=5.0)
            conn.execute('PRAGMA journal_mode = WAL')
            conn.execute('PRAGMA synchronous = NORMAL')
            self.pool.put(conn)
            
    @contextmanager
    def get_connection(self):
        conn = self.pool.get()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.put(conn)

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()


class PasswordRepository:
    """密碼資料存取"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance
    
    def _init_db(self):
        """初始化資料庫"""
        Config.ensure_dirs()
        self._pool = SQLitePool(str(Config.DB_FILE))
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def _check_auth(self):
        """啟動前驗證認證狀態"""
        if not session.is_authenticated():
            raise PermissionError("未經授權的存取：請先完成 Windows 認證")

    @contextmanager
    def _get_conn(self):
        """取得資料庫連線 (從連線池)"""
        with self._pool.get_connection() as conn:
            yield conn
    
    def add(self, service: str, username: str, password: str) -> bool:
        """新增密碼"""
        self._check_auth()
        try:
            encrypted = encrypt(password)
            now = datetime.now()
            with self._get_conn() as conn:
                conn.execute(
                    'INSERT INTO passwords (service, username, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                    (service, username, encrypted, now, now)
                )
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get(self, service: str) -> Optional[Dict]:
        """取得單一密碼"""
        self._check_auth()
        with self._get_conn() as conn:
            row = conn.execute(
                'SELECT id, service, username, password, updated_at FROM passwords WHERE service = ?',
                (service,)
            ).fetchone()
        
        if row:
            return {
                'id': row[0],
                'service': row[1],
                'username': row[2],
                'password': decrypt(row[3]),
                'updated_at': row[4]
            }
        return None
    
    def get_all(self) -> List[Dict]:
        """取得所有密碼 (不含密碼明文)"""
        self._check_auth()
        with self._get_conn() as conn:
            rows = conn.execute(
                'SELECT id, service, username, updated_at FROM passwords ORDER BY updated_at DESC'
            ).fetchall()
        
        return [{'id': r[0], 'service': r[1], 'username': r[2], 'updated_at': r[3]} for r in rows]
    
    def update(self, service: str, username: str, password: str) -> bool:
        """更新密碼"""
        self._check_auth()
        encrypted = encrypt(password)
        with self._get_conn() as conn:
            cursor = conn.execute(
                'UPDATE passwords SET username = ?, password = ?, updated_at = ? WHERE service = ?',
                (username, encrypted, datetime.now(), service)
            )
        return cursor.rowcount > 0
    
    def delete(self, service: str) -> bool:
        """刪除密碼"""
        self._check_auth()
        with self._get_conn() as conn:
            cursor = conn.execute('DELETE FROM passwords WHERE service = ?', (service,))
        return cursor.rowcount > 0
    
    def export_csv(self, file_path: str) -> bool:
        """導出為 CSV"""
        self._check_auth()
        import csv
        with self._get_conn() as conn:
            rows = conn.execute(
                'SELECT service, username, password, updated_at FROM passwords ORDER BY updated_at DESC'
            ).fetchall()
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['服務名稱', '用戶名', '密碼', '最後修改日期'])
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    '服務名稱': row[0],
                    '用戶名': row[1],
                    '密碼': decrypt(row[2]),
                    '最後修改日期': row[3]
                })
        return True
