from config import load_settings, AdminConfig

from .database import DatabaseManager
from .repositories import (
    DialogRepository,
    MessageRepository,
    ProductRepository,
    UserRepository,
    ShopCardItemRepository,
    ShopCardRepository
)

db_settings, _ = load_settings()
admin_config = AdminConfig(admin_ids=[794764254])

db_manager = DatabaseManager(
    config=db_settings,
    echo=False,
    pool_size=10,
    repositories=[
        UserRepository,
        ProductRepository,
        DialogRepository,
        MessageRepository,
        ShopCardRepository,
        ShopCardItemRepository,
    ],
)

__all__ = ["db_manager", "admin_config"]
