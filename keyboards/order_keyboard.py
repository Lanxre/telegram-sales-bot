from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.internal.enums import CallbackPrefixes


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


def get_status_order_keyboard(order_id: int) -> ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Выполнить", callback_data=f"{CallbackPrefixes.ORDER_STATUS_CONFIRM.value}{order_id}"
    )
    builder.button(
        text="❌ Отменить", callback_data=f"{CallbackPrefixes.ORDER_STATUS_CANSEL.value}{order_id}"
    )
    return builder.as_markup()
