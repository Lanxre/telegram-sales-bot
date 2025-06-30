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
