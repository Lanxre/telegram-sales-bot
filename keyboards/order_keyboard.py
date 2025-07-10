from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить заказ")],
            [KeyboardButton(text="❌ Отменить оформление")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_order_confirm_keyboard() -> ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="final_confirm")
    builder.button(text="❌ Отменить", callback_data="order_cancel")
    return builder.as_markup()
