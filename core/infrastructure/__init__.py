from config import load_settings
from .database import DatabaseManager
from .repositories import UserRepository, ProductRepository

db_settings, _ = load_settings()

db_manager = DatabaseManager(
    config=db_settings,
    echo=False,
    repositories=[UserRepository, ProductRepository]
)

__all__ = ["db_manager"]