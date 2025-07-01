from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_dialog_keyboard() -> ReplyKeyboardMarkup:
    dialog_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Завершить диалог")],
            [KeyboardButton(text="📋 Показать историю")],
        ],
        resize_keyboard=True,
    )
    return dialog_keyboard
