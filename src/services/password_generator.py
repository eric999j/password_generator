"""
密碼生成服務
"""

import string
import secrets
from src.config import Config


class PasswordGenerator:
    """密碼生成器"""

    CHARS_BASIC = string.ascii_letters + string.digits
    CHARS_FULL = CHARS_BASIC + string.punctuation
    LOWER_CHARS = set(string.ascii_lowercase)
    UPPER_CHARS = set(string.ascii_uppercase)
    DIGIT_CHARS = set(string.digits)
    SPECIAL_CHARS = set(string.punctuation)
    
    @classmethod
    def generate(cls, level: str = '中') -> str:
        """
        生成密碼
        
        Args:
            level: 強度等級 ('低', '中', '高')
        """
        cfg = Config.STRENGTH_LEVELS.get(level, Config.STRENGTH_LEVELS['中'])
        chars = cls.CHARS_FULL if cfg['use_special'] else cls.CHARS_BASIC
        return ''.join(secrets.choice(chars) for _ in range(cfg['length']))
    
    @classmethod
    def evaluate(cls, password: str) -> tuple:
        """
        評估密碼強度
        
        Returns:
            (分數 0-100, 顏色, 等級文字)
        """
        if not password:
            return 0, '#FF4444', '---'

        score = min(len(password) * 5, 30)

        # 單次掃描：同時統計字符多樣性與連續字符扣分
        has_lower = False
        has_upper = False
        has_digit = False
        has_special = False

        prev2_ord = None
        prev1_ord = None
        prev2_isalnum = False
        prev1_isalnum = False

        for ch in password:
            if not has_lower and ch in cls.LOWER_CHARS:
                has_lower = True
            elif not has_upper and ch in cls.UPPER_CHARS:
                has_upper = True
            elif not has_digit and ch in cls.DIGIT_CHARS:
                has_digit = True
            elif not has_special and ch in cls.SPECIAL_CHARS:
                has_special = True

            current_ord = ord(ch)
            current_isalnum = ch.isalnum()
            if prev2_ord is not None and prev2_isalnum and prev1_isalnum and current_isalnum:
                delta1 = prev1_ord - prev2_ord
                delta2 = current_ord - prev1_ord
                # 檢查遞增或遞減序列
                if (delta1 == 1 and delta2 == 1) or (delta1 == -1 and delta2 == -1):
                    score -= 10

            prev2_ord = prev1_ord
            prev1_ord = current_ord
            prev2_isalnum = prev1_isalnum
            prev1_isalnum = current_isalnum

        score += (has_lower + has_upper + has_digit + has_special) * 15
        score = max(0, min(score, 100))
        
        # 判定等級
        if score <= Config.STRENGTH_WEAK_THRESHOLD:
            return score, '#FF4444', '弱'
        elif score <= Config.STRENGTH_MEDIUM_THRESHOLD:
            return score, '#FFAA44', '中'
        else:
            return score, '#44AA44', '強'
