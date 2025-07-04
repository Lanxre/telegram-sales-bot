from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить заказ")],
            [KeyboardButton(text="❌ Отменить оформление")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
