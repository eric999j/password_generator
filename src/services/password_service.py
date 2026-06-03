"""密碼應用服務層。"""

from typing import Dict, List, Optional

from src.crypto.secure_string import SecureString
from src.database import PasswordRepository


class PasswordService:
    """封裝密碼管理用例，隔離 GUI 與資料層。"""

    def __init__(self, repository: Optional[PasswordRepository] = None):
        self._repository = repository or PasswordRepository()

    @staticmethod
    def _normalize_input(service: str, username: str, password: str) -> tuple[str, str, str]:
        return service.strip(), username.strip(), password.strip()

    def create_password(self, service: str, username: str, password: str) -> bool:
        service, username, password = self._normalize_input(service, username, password)
        if not service or not username or not password:
            return False

        with SecureString(password) as sec_pwd:
            return self._repository.add(service, username, sec_pwd.get_value())

    def update_password(self, service: str, username: str, password: str) -> bool:
        service, username, password = self._normalize_input(service, username, password)
        if not service or not username or not password:
            return False

        with SecureString(password) as sec_pwd:
            return self._repository.update(service, username, sec_pwd.get_value())

    def get_password(self, service: str) -> Optional[Dict]:
        service = service.strip()
        if not service:
            return None
        return self._repository.get(service)

    def get_all_passwords(self) -> List[Dict]:
        return self._repository.get_all()

    def delete_password(self, service: str) -> bool:
        service = service.strip()
        if not service:
            return False
        return self._repository.delete(service)

    def export_csv(self, file_path: str) -> bool:
        return self._repository.export_csv(file_path)
