from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.infrastructure import db_manager
from core.infrastructure.services import (
    CatalogService,
    ShopService,
)
from core.internal.models import ProductCreate
from filters import IsAdmin
from utils import ImageSelector, StateToModel

from .states import AddProduct

product_add_router = Router()
shop_service = ShopService(db_manager)
catalog_service = CatalogService(shop_service)


@product_add_router.message(Command("addproduct"), IsAdmin())
async def command_add_product(message: Message, state: FSMContext) -> None:
    await message.answer("Пожалуйста введите название предмета.")
    await state.set_state(AddProduct.waiting_for_name)


@product_add_router.message(AddProduct.waiting_for_name)
async def process_product_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()

    if not name:
        await message.answer("Название не должно быть пустым.")
        return

    await state.update_data(name=name)
    await message.answer(
        "Пожайлуста введите описание предмета (или введите 'skip' для пропуска)."
    )
    await state.set_state(AddProduct.waiting_for_description)


@product_add_router.message(AddProduct.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext) -> None:
    description = message.text.strip()

    if description.lower() == "skip":
        description = None

    await state.update_data(description=description)
    await message.answer("Пожайлуста введите стоимость предмета (напр., 19.99).")
    await state.set_state(AddProduct.waiting_for_price)


@product_add_router.message(AddProduct.waiting_for_price)
async def process_product_price(message: Message, state: FSMContext) -> None:
    price_text = message.text.strip()
    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError("Цена должна быть положительной.")
    except ValueError:
        await message.answer("Введите коректную цену (напр., 19.99).")
        return

    await state.update_data(price=price)
    await message.answer(
        "Пожайлуста оправьте изображение предмета (или введите 'skip' для пропуска)."
    )
    await state.set_state(AddProduct.waiting_for_image)


@product_add_router.message(AddProduct.waiting_for_image)
async def process_product_image(message: Message, state: FSMContext, bot: Bot) -> None:
    image_bytes = await ImageSelector.get_image_bytes(message, bot)

    product_data: ProductCreate = await StateToModel.from_context(state, ProductCreate)
    product_data.image = image_bytes.read()

    try:
        product = await shop_service.add_product(product_data)
        await message.answer(
            f"Предмет добавлен в каталог: {product.name} (ID: {product.id}, Price: {product.price}$)"
        )

    except Exception as e:
        await message.answer(f"Ошибка при добавление предмета: {str(e)}")
    await state.clear()
