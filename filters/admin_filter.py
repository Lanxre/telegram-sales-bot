from typing import List, Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message

from logger import LoggerBuilder
from utils import StringBuilder

logger = LoggerBuilder("ADMIN FILTER").add_stream_handler().build()


def get_admins_ids() -> Optional[List[int]]:
    with open("admin_ids.txt", "r", encoding="utf-8") as f:
        try:
            ids = f.readline().split(",")
            ADMIN_IDS = [int(x) for x in ids]

            builder = StringBuilder()
            for i, admin_id in enumerate(ids, 1):
                builder.append(f"{i}. {admin_id}, ")

            logger.info(f"Admins ids: {builder.to_string()}")
            return ADMIN_IDS
        except Exception as e:
            raise e


class IsAdmin(BaseFilter):
    def __init__(self):
        super().__init__()
        self.ADMIN_IDS = get_admins_ids()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.ADMIN_IDS