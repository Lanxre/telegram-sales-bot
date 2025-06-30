from aiogram import Bot, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.infrastructure import db_manager
from core.infrastructure.services import (
    CatalogService,
    ShopService,
)
from core.internal.models import ProductUpdate
from utils import ImageSelector

from .states import EditProduct

product_edit_router = Router()
shop_service = ShopService(db_manager)
catalog_service = CatalogService(shop_service)


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_name_"))
async def proccess_edit_name(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await callback.message.answer("Введите название продукта")
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_name)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_name)
async def process_edit_name(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    product_id = data["product_id"]
    user_message = message.text.strip()

    if user_message.lower() == "skip":
        await message.answer("Название не изменено")
        await state.clear()
        return

    try:
        await shop_service.update_product(
            product_id=product_id, product_data=ProductUpdate(name=user_message)
        )
        await message.answer(f"Название изменено на: {html.bold(message.text)}")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

    await state.clear()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_desc_"))
async def proccess_edit_descriprion(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await callback.message.answer("Введите описание продукта")
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_description)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_description)
async def process_edit_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    product_id = data["product_id"]
    user_message = message.text.strip()

    if user_message.lower() == "skip":
        await message.answer("Описание не изменено")
        await state.clear()
        return

    try:
        await shop_service.update_product(
            product_id=product_id, product_data=ProductUpdate(description=user_message)
        )
        await message.answer("Описание успешно обновлено!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

    await state.clear()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_price_"))
async def proccess_edit_price(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await callback.message.answer("Введите цену продукта")
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_price)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_price)
async def process_edit_price(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    product_id = data["product_id"]

    if message.text.strip().lower() == "skip":
        await message.answer("Цена не изменена")
        await state.clear()
        return

    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError("Цена должна быть положительной")

        await shop_service.update_product(
            product_id=product_id, product_data=ProductUpdate(price=price)
        )
        await message.answer(f"Цена изменена на: {html.bold(price)}$")
    except ValueError:
        await message.answer("Введите корректную цену (например: 19.99)")
        return

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

    await state.clear()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_image_"))
async def proccess_edit_image(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await callback.message.answer("Загрузите картинку продукта")
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_image)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_image)
async def process_edit_image(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    product_id = data["product_id"]

    if message.text and message.text.strip().lower() == "skip":
        await message.answer("Изображение не изменено")
        await state.clear()
        return

    if not message.photo:
        await message.answer("Пожалуйста, отправьте изображение или введите 'skip'")
        return

    try:
        image_bytes = await ImageSelector.get_image_bytes(message, bot)
        await shop_service.update_product(
            product_id=product_id, product_data=ProductUpdate(image=image_bytes.read())
        )
        await message.answer("Изображение успешно обновлено!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

    await state.clear()
