import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_settings
from dispatcher import create_dispatcher
from logger import LoggerBuilder

from data import CommandList

logger = LoggerBuilder("TelegramBot").add_stream_handler().build()

db_settings, telegram_settings = load_settings()


async def main() -> None:
    dp = create_dispatcher()
    bot = Bot(
        token=telegram_settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Set commands 
    commands = CommandList()
    commands.load_from_json("./data/command_list.json")
    await bot.set_my_commands(commands=commands.get_commands())


    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Bot start")
    asyncio.run(main())
