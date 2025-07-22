from enum import Enum


class ButtonText(str, Enum):
    FINISH_DIALOG = "📝 Завершить диалог"


class InlineQueryText(str, Enum):
    CATALOG = "catalog"


class CallbackqueryText(str, Enum):
    ORDER_CONFIRM = "order_confirm"
    ORDER_FINAL_CONFIRM = "final_confirm"
    ORDER_CANSEL = "order_cancel"
    ORDER_RECEIVED = "received_orders"


class CallbackPrefixes(str, Enum):
    DIALOG_APPEALS = "dialog_apeals_"
    ANSWER_APPEALS = "answer_apeals_"

    CATALOG_INIT = "catalog_"

    PRODUCT_DELETE = "confirm_delete_"
    PRODUCT_CANSEL_DELETE = "cancel_delete_"
    PRODUCT_EDIT_NAME = "edit_name_"
    PRODUCT_EDIT_DESCRIPTION = "edit_desc_"
    PRODUCT_EDIT_PRICE = "edit_price_"
    PRODUCT_EDIT_IMAGE = "edit_image_"

    SHOPCARD_ADD = "shopcard_add_"
    SHOPCARD_DELETE = "shopcard_delete_item_"
    SHOPCARD_ITEM_INCREMENT = "shopcard_item_inc_"
    SHOPCARD_ITEM_DECREMENT = "shopcard_item_dec_"
    SHOPCARD_ITEM_PREV = "shopcard_item_prev_"
    SHOPCARD_ITEM_NEXT = "shopcard_item_next_"

    ORDER_RECEIVED = "received_orders_"
    ORDER_RECEIVED_NEXT = "received_orders_next_"
    ORDER_RECEIVED_PREV = "received_orders_prev_"
    ORDER_STATUS_CONFIRM = "received_order_confirm_"
    ORDER_STATUS_CANSEL = "received_order_cansel_"

    @classmethod
    def has_any_prefix(cls, callback_data: str) -> bool:
        return any(callback_data.startswith(item.value) for item in cls)

    @classmethod
    def has_prefix(cls, callback_data: str, prefix: str) -> bool:
        return callback_data.startswith(prefix)

    @staticmethod
    def extract_numbers_after_prefix(callback_data: str, prefix: str) -> list[int]:
        if not callback_data.startswith(prefix):
            return []

        parts = callback_data[len(prefix) :].split("_")
        return [int(p) for p in parts if p.isdigit()]

    @staticmethod
    def last_index_after_prefix(callback_data: str, prefix: str) -> int:
        data = CallbackPrefixes.extract_numbers_after_prefix(callback_data, prefix)
        return data[-1]
