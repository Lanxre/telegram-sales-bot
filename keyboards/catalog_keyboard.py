from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_catalog_keyboard(
    current_index: int, 
    total_products: int, 
    is_admin: bool = False
) -> InlineKeyboardMarkup:
    """
    Generates a paginated catalog keyboard with navigation and admin controls.
    
    Args:
        current_index: Current product index (0-based).
        total_products: Total number of products.
        is_admin: Whether to show admin buttons (delete/edit).

    Returns:
        InlineKeyboardMarkup with buttons organized in logical rows.
    """
   
    navigation_buttons = []
    if current_index > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущий", 
                callback_data=f"catalog_prev_{current_index}"
            )
        )
    
    if current_index < total_products - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Следующий ➡️", 
                callback_data=f"catalog_next_{current_index}"
            )
        )

    
    admin_buttons = []
    if is_admin:
        admin_buttons.extend([
            InlineKeyboardButton(
                text="Удалить ❌", 
                callback_data=f"catalog_delete_{current_index}"
            ),
            InlineKeyboardButton(
                text="Редактировать ✏️", 
                callback_data=f"catalog_edit_{current_index}"
            )
        ])

    # Combine rows (filter empty rows)
    keyboard = [
        row for row in [navigation_buttons, admin_buttons] 
        if row  # Skip empty rows
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_delete_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"confirm_delete_{product_id}")
    builder.adjust(2)
    return builder.as_markup()
