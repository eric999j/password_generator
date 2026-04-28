# -*- mode: python ; coding: utf-8 -*-
import sys
import os

"""
PyInstaller spec configuration file
支援跨平台 (Windows, Mac, Linux) 打包
"""

block_cipher = None

# 根據平台決定隱藏導入
hidden_imports = [
    'cryptography',
    'sqlite3',
    'tkinter',
    'ttkbootstrap',
    'keyring',
    'src',
    'src.config',
    'src.auth',
    'src.auth.system_auth',
    'src.auth.session',
    'src.crypto',
    'src.crypto.encryption',
    'src.crypto.platform_security',
    'src.crypto.secure_string',
    'src.database',
    'src.database.repository',
    'src.services',
    'src.services.password_generator',
    'src.gui',
    'src.gui.app',
]

if sys.platform == 'win32':
    hidden_imports += ['ctypes', 'ctypes.wintypes']
elif sys.platform == 'linux':
    hidden_imports += ['pamela', 'secretstorage']
elif sys.platform == 'darwin':
    hidden_imports += ['pamela']

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='強密碼產生器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
