from config import load_settings

from .database import DatabaseManager
from .repositories import (
    DialogRepository,
    MessageRepository,
    ProductRepository,
    UserRepository,
)

db_settings, _ = load_settings()

db_manager = DatabaseManager(
    config=db_settings,
    echo=False,
    pool_size=10,
    repositories=[
        UserRepository,
        ProductRepository,
        DialogRepository,
        MessageRepository,
    ],
)

__all__ = ["db_manager"]
