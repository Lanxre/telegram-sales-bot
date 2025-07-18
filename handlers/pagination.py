from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from core.internal.types import PaginationData
from utils import StringBuilder


async def create_pagination(
    message: Message | CallbackQuery, pagination_data: PaginationData
) -> None:
    
    if not len(pagination_data.items):
        await message.answer("Заказов больше нет!", show_alert=True)
        return
    
    text = await _generate_text_pagination(
        pagination_data.text, pagination_data.items, pagination_data.page
    )
  
    keyboard = await _get_pagination_keyboard(
        pagination_data.callback_name,
        pagination_data.items,
        pagination_data.page,
        pagination_data.page_size,
    )

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text=text, reply_markup=keyboard)
        
    else:
        await message.answer(text, reply_markup=keyboard)


async def _generate_text_pagination(answer_text: str, items: list, page: int) -> str:
    text = StringBuilder(answer_text)
    text.append("\n")

    if items:
        text.append(f"Страница: {page + 1}")
        text.append("\n")

    text.append(f"Общее кол-во: {len(items)}")
    return text.to_string()


async def _get_pagination_keyboard(
    callback_name: str, items: list, current_page: int, page_size: int
) -> InlineKeyboardMarkup:
    total_items = len(items)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    await _paginate_items(keyboard, items, callback_name, page_size)
    await _set_nav_buttons(
        keyboard, total_items, callback_name, current_page, page_size
    )

    return keyboard


async def _paginate_items(
    keyboard: InlineKeyboardMarkup, items: list, callback_name: str, page_size: int
) -> None:
    buttons = [
        InlineKeyboardButton(
            text=f"{item.id}", callback_data=f"{callback_name}_{item.id}"
        )
        for item in items[:page_size]
    ]

    for i in range(0, len(buttons), page_size):
        keyboard.inline_keyboard.append(buttons[i : i + page_size])


async def _set_nav_buttons(
    keyboard: InlineKeyboardMarkup,
    total_items: int,
    callback_name: str,
    current_page: int,
    page_size: int
) -> None:

    nav_buttons = []

    if current_page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущая",
                callback_data=f"{callback_name}_prev_{page_size}_{current_page - 1}",
            )
        )

    if total_items:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Следующая ➡️",
                callback_data=f"{callback_name}_next_{page_size}_{current_page + 1}",
            )
        )

    if nav_buttons:
        keyboard.inline_keyboard.append(nav_buttons)