from aiogram.fsm.state import State, StatesGroup


class ProductImageUpdate(StatesGroup):
    waiting_for_image = State()


class AddProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image = State()


class EditProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image = State()


class DialogStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_answer_apeals = State()

class OrderConfirm(StatesGroup):
    waiting_for_order_note = State()
    waiting_for_address_delivery = State()