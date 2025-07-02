from typing import List

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from core.infrastructure.database.models import Dialog


def get_dialog_keyboard() -> ReplyKeyboardMarkup:
    dialog_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Завершить диалог")],
            [KeyboardButton(text="📋 Показать историю")],
        ],
        resize_keyboard=True,
    )

    return dialog_keyboard


def get_apeals_keyboard(dialogs: List[Dialog]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    buttons = [
        InlineKeyboardButton(
            text=f"{dialog.user1_id}", callback_data=f"dialog_apeals_{dialog.id}"
        )
        for dialog in dialogs
    ]

    for i in range(0, len(buttons), 5):
        keyboard.inline_keyboard.append(buttons[i : i + 5])

    return keyboard


def get_message_keyboard(dialog: Dialog) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Нажмите, что бы ответить на обращение",
                    callback_data=f"answer_apeals_{dialog.id}",
                )
            ]
        ]
    )
