from config import load_settings
from .database import DatabaseManager
from .repositories import UserRepository

db_settings, _ = load_settings()

db_manager = DatabaseManager(
    config=db_settings,
    echo=True,
    repositories=[UserRepository]
)

__all__ = ["db_manager"]