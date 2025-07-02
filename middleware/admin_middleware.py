from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import AdminConfig
from logger import LoggerBuilder

logger = LoggerBuilder("AdminMiddleware").add_stream_handler().build()


class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_config: AdminConfig):
        self.admin_config = admin_config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            if isinstance(event, (Message, CallbackQuery)):
                data["is_admin"] = self.admin_config.is_admin(event.from_user.id)
                state = data.get("state")
                if state:
                    await state.update_data(is_admin=data["is_admin"])

            return await handler(event, data)
        except Exception as e:
            logger.error(f"AdminMiddleware error: {e}")
