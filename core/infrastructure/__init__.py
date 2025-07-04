from config import AdminConfig, load_settings

from .database import DatabaseManager
from .repositories import (
    DialogRepository,
    MessageRepository,
    OrderRepository,
    ProductRepository,
    ShopCardItemRepository,
    ShopCardRepository,
    UserRepository,
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
        OrderRepository,
    ],
)

__all__ = ["db_manager", "admin_config"]
