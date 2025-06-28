from io import BytesIO
from typing import BinaryIO, Optional
from aiogram import Bot
from aiogram.types import Message, BufferedInputFile


class ImageSelector:
    def __new__(cls) -> None:
        raise TypeError(f"{cls.__name__} is a static class and cannot be instantiated.")

    @staticmethod
    async def get_image_bytes(message: Message, bot: Bot) -> Optional[BinaryIO]:
        
        if not message.photo:
            raise ValueError("Message does not contain a photo.")
        
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        return await bot.download_file(file.file_path)

    @staticmethod
    async def get_image_file(image: bytes, file_name: str) -> BufferedInputFile:
        image_stream = BytesIO(image)
        image_file = BufferedInputFile(
            image_stream.getvalue(), filename=file_name
        )
        return image_file