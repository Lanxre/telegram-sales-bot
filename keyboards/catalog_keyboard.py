from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_catalog_keyboard(
    current_index: int, total_products: int
) -> InlineKeyboardMarkup:
    buttons = []
    # Add Previous button (disabled if at first product)
    if current_index > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущий", callback_data=f"catalog_prev_{current_index}"
            )
        )

    # Add Next button (disabled if at last product)
    if current_index < total_products - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Следующий ➡️", callback_data=f"catalog_next_{current_index}"
            )
        )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
