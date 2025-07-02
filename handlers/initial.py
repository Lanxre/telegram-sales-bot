from aiogram import Router, html
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from core.infrastructure.services import ShopService
from core.internal.models import UserCreate
from data import CommandList

initial_router = Router()


@initial_router.message(CommandStart())
async def command_start(message: Message, shop_service: ShopService) -> None:
    try:
        await shop_service.create_user(
            UserCreate(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
            )
        )
        await message.answer(
            f"Приветсвую тебя {html.bold(message.from_user.full_name)}, этот бот создан для продажи моих предметов!\n"
            + "Для списка всех команд используй /help",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        await message.answer(
            f"Что-то пошло не так! {str(e)}",
            reply_markup=ReplyKeyboardRemove(),
        )


@initial_router.message(Command("help"))
async def command_help(message: Message) -> None:
    commands = CommandList()
    await message.answer(f"{commands.to_string()}", reply_markup=ReplyKeyboardRemove())
