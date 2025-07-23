from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram_i18n import I18nContext

from core.infrastructure.services import ShopService
from core.internal.models import UserCreate
from data import CommandList

initial_router = Router()


@initial_router.message(CommandStart())
async def command_start(
    message: Message, shop_service: ShopService, i18n: I18nContext
) -> None:
    try:
        await shop_service.create_user(
            UserCreate(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
            )
        )
        await message.answer(
            text=i18n.get(
                "greeting",
                message.from_user.language_code,
                user_full_name=message.from_user.full_name,
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        await message.answer(
            text=i18n.get(
                "initial_router_error", message.from_user.language_code, error=str(e)
            ),
            reply_markup=ReplyKeyboardRemove(),
        )


@initial_router.message(Command("help"))
async def command_help(message: Message) -> None:
    commands = CommandList()
    await message.answer(f"{commands.to_string()}", reply_markup=ReplyKeyboardRemove())
