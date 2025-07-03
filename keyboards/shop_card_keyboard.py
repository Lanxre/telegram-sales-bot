from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_shop_card_keyboard(
    current_index: int, product_id: int, total_products: int
) -> InlineKeyboardMarkup:
    navigation_buttons = []
    if current_index > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущий", callback_data=f"shopcard_item_prev_{current_index}_{product_id}"
            )
        )

    if current_index < total_products - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Следующий ➡️", callback_data=f"shopcard_item_next_{current_index}_{product_id}"
            )
        )

    count_buttons = [
        InlineKeyboardButton(
            text="⬅️ Уменьшить кол-во",
            callback_data=f"shopcard_item_dec_{current_index}_{product_id}",
        ),
        InlineKeyboardButton(
            text="Увеличить кол-во ➡️",
            callback_data=f"shopcard_item_inc_{current_index}_{product_id}",
        ),
    ]

    shop_card_button = [
        InlineKeyboardButton(
            text="Удалить из корзины ❌",
            callback_data=f"shopcard_delete_item_{product_id}",
        ),
        InlineKeyboardButton(text="Потвердить заказ ✏️", callback_data="order_confirm"),
    ]

    keyboard = [row for row in [navigation_buttons, count_buttons, shop_card_button] if row]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
