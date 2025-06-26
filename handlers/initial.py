from aiogram import Router, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from data import CommandList

initial_router = Router()

@initial_router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer(
        f"Приветсвую тебя {html.bold(message.from_user.full_name)}, этот бот создан для продажи моих предметов!\n" + \
        "Для списка всех команд используй /help",
        reply_markup=ReplyKeyboardRemove()
    )


@initial_router.message(Command("help"))
async def command_help(message: Message) -> None:
    commands = CommandList()
    await message.answer(
        f"{commands.to_string()}",
        reply_markup=ReplyKeyboardRemove()
    )