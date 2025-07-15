from functools import wraps
from aiogram.types import CallbackQuery
from logger import LoggerBuilder

logger = LoggerBuilder("Handler").add_stream_handler().build()


def handle_shopcard_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        callback = next(arg for arg in args if isinstance(arg, CallbackQuery))
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            await callback.answer("❌ Произошла ошибка", show_alert=True)

    return wrapper
