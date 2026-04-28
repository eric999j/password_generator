"""
SecureString 模擬
用於減少敏感資料在記憶體中的明文暴露時間
"""

import gc
import ctypes

class SecureString:
    """
    簡單的 SecureString 模擬
    使用 bytearray 並在銷毀時嘗試抹除記憶體
    """
    def __init__(self, value: str):
        self._data = bytearray(value.encode('utf-8'))
        
    def get_value(self) -> str:
        """取得字串值 (使用後應盡快銷毀)"""
        return self._data.decode('utf-8')
    
    def clear(self):
        """抹除記憶體中的資料並強制 GC"""
        if self._data:
            # 1. 逐位元組覆寫為 0
            for i in range(len(self._data)):
                self._data[i] = 0
            self._data = None
            
            # 2. 強制執行垃圾回收
            gc.collect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def __del__(self):
        self.clear()
