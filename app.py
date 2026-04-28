"""
強密碼產生器 - 入口點
"""
import sys
sys.path.insert(0, '.')

from src.auth import authenticate_user
from src.gui import run_app

if __name__ == '__main__':
    if not authenticate_user():
        sys.exit(1)
    run_app()
