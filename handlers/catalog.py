from io import BytesIO

from aiogram import Bot, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message

from core.infrastructure import db_manager
from core.infrastructure.services import ShopService
from core.internal.models import ProductCreate
from filters import IsAdmin
from keyboards import get_catalog_keyboard
from utils import ImageSelector, StateToModel

from .states import AddProduct

catalog_router = Router()
shop_service = ShopService(db_manager)


@catalog_router.message(Command("catalog"))
async def command_catalog(message: Message) -> None:
    products = await shop_service.get_all_products()

    if not products:
        await message.answer("Нет предметов для продажи")
        return

    current_index = 0
    product = products[current_index]

    caption = (
        f"Название: {html.bold(product.name)}\n\n"
        f"Описание: {html.italic(product.description or 'Нет описания')}\n\n"
        f"Стоимость: {product.price}$"
    )

    if product.image:
        image_stream = BytesIO(product.image)
        image_file = BufferedInputFile(
            image_stream.getvalue(), filename=f"product_{product.id}.jpg"
        )
        await message.answer_photo(
            photo=image_file,
            caption=caption,
            reply_markup=get_catalog_keyboard(current_index, len(products)),
        )
    else:
        await message.answer(
            text=caption,
            reply_markup=get_catalog_keyboard(current_index, len(products)),
        )


@catalog_router.callback_query(lambda c: c.data.startswith("catalog_"))
async def process_catalog_navigation(callback: CallbackQuery, bot: Bot) -> None:
    # Extract action and current index from callback data
    action, current_index = (
        callback.data.split("_")[1],
        int(callback.data.split("_")[2]),
    )

    # Get all products
    products = await shop_service.get_all_products()
    if not products:
        await callback.message.edit_text("Нет предметов для продажи")
        await callback.answer()
        return

    # Calculate new index
    new_index = current_index
    if action == "prev" and current_index > 0:
        new_index = current_index - 1
    elif action == "next" and current_index < len(products) - 1:
        new_index = current_index + 1

    # Get the new product
    product = products[new_index]

    # Prepare caption
    caption = (
        f"Название: {html.bold(product.name)}\n\n"
        f"Описание: {html.italic(product.description or 'Нет описания')}\n\n"
        f"Стоимость: {product.price}$"
    )

    # Prepare inline keyboard
    keyboard = get_catalog_keyboard(new_index, len(products))

    # Update the message
    try:
        if product.image:
            image_file = ImageSelector.get_image_file(
                product.image, f"product_{product.id}.jpg"
            )
            await bot.edit_message_media(
                media=InputMediaPhoto(media=image_file, caption=caption),
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard,
            )
        else:
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=caption,
                reply_markup=keyboard,
            )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка в обработке предмета: {str(e)}")

    await callback.answer()


@catalog_router.message(Command("add_product"), IsAdmin())
async def command_add_product(message: Message, state: FSMContext) -> None:
    await message.answer("Пожалуйста введите название предмета.")
    await state.set_state(AddProduct.waiting_for_name)


@catalog_router.message(AddProduct.waiting_for_name)
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


@catalog_router.message(AddProduct.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext) -> None:
    description = message.text.strip()

    if description.lower() == "skip":
        description = None

    await state.update_data(description=description)
    await message.answer("Пожайлуста введите стоимость предмета (напр., 19.99).")
    await state.set_state(AddProduct.waiting_for_price)


@catalog_router.message(AddProduct.waiting_for_price)
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


@catalog_router.message(AddProduct.waiting_for_image)
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

