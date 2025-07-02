from time import time

from config import AdminConfig
from logger import LoggerBuilder

logger = LoggerBuilder("ADMIN FILTER").add_stream_handler().build()


class AdminService:
    def __init__(self, admin_config: AdminConfig):
        self.admin_config = admin_config

    async def reload_admins(self) -> None:
        self.admin_config._load_admin_ids()

    async def add_admin(self, user_id: int) -> bool:
        if user_id not in self.admin_config.admin_ids:
            self.admin_config.admin_ids.append(user_id)
            self._save_admin_ids()
            return True
        return False

    def _save_admin_ids(self) -> None:
        try:
            with open(self.admin_config.config_path, "w", encoding="utf-8") as f:
                f.write(",".join(map(str, self.admin_config.admin_ids)))
            self.admin_config._last_updated = time()
        except Exception as e:
            logger.error(f"Failed to save admin IDs: {e}")
            raise