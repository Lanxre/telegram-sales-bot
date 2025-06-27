from aiogram.filters import BaseFilter
from aiogram.types import Message

from logger import LoggerBuilder
from utils import StringBuilder

logger = LoggerBuilder("ADMIN FILTER").add_stream_handler().build()

ADMIN_IDS = []

with open("admin_ids.txt", "r", encoding="utf-8") as f:
    try:
        ids = f.readline().split(",")
        ADMIN_IDS = [int(x) for x in ids]

        builder = StringBuilder()
        for i, admin_id in enumerate(ids, 1):
            builder.append(f"{i}. {admin_id}, ")

        logger.info(f"Admins ids: {builder.to_string()}")

    except Exception as e:
        raise e


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("This command is restricted to admins.")

        return message.from_user.id in ADMIN_IDS
