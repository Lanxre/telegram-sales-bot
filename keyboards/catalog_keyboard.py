from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_catalog_keyboard(
    current_index: int,
    product_id: int, 
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

    shop_card_button = [InlineKeyboardButton(
        text="Добавить в корзину 🛒",
        callback_data=f"shoppcard_{product_id}"
    )]

    # Combine rows (filter empty rows)
    keyboard = [
        row for row in [navigation_buttons, shop_card_button, admin_buttons] 
        if row  # Skip empty rows
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_delete_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"confirm_delete_{product_id}")
    builder.button(text="❌ Отменить", callback_data=f"cancel_delete_{product_id}") 
    builder.adjust(2)
    return builder.as_markup()

def get_edit_keyboard(product_id: int, current_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Название", callback_data=f"edit_name_{product_id}")
    builder.button(text="📝 Описание", callback_data=f"edit_desc_{product_id}")
    builder.button(text="💵 Цена", callback_data=f"edit_price_{product_id}")
    builder.button(text="🖼️ Изображение", callback_data=f"edit_image_{product_id}")
    builder.button(text="⬅️ Назад", callback_data=f"catalog_prev_{current_index + 1}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()