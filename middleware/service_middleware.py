from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config import AdminConfig
from core.infrastructure.database import DatabaseManager
from core.infrastructure.services import CatalogService, DialogService, ShopService


class ServiceMiddleware(BaseMiddleware):
    def __init__(
        self, db_manager: DatabaseManager, admin_config: Optional[AdminConfig] = None
    ):
        self.db_manager = db_manager
        self.admin_config = admin_config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        services = {
            "dialog_service": DialogService(self.db_manager, self.admin_config),
            "catalog_service": CatalogService(ShopService(self.db_manager)),
            "shop_service": ShopService(self.db_manager),
        }

        data.update(services)
        result = await handler(event, data)
        return result
