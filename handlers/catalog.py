from aiogram import Bot, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from core.infrastructure import db_manager
from core.infrastructure.services import (
    CaptionStrategyType,
    CatalogService,
    DeleteCaptionArgs,
    ProductCaptionArgs,
    ShopService,
)
from core.internal.models import ProductCreate
from filters import IsAdmin
from keyboards import get_catalog_keyboard, get_confirm_delete_keyboard
from utils import ImageSelector, StateToModel

from .states import AddProduct

catalog_router = Router()
shop_service = ShopService(db_manager)
catalog_service = CatalogService(shop_service)


@catalog_router.message(Command("catalog"))
async def command_catalog(message: Message) -> None:
    try:
        products = await catalog_service.get_products()

        if not products:
            await message.answer(catalog_service.config.no_products_text)
            return

        product = products[0]
        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.PRODUCT,
            args=ProductCaptionArgs(product=product),
        )
        is_admin = await IsAdmin()(message)

        if image_file := await catalog_service.get_product_image(product.id, product):
            await message.answer_photo(
                photo=image_file,
                caption=caption,
                reply_markup=get_catalog_keyboard(0, len(products), is_admin),
            )
        else:
            await message.answer(
                text=caption,
                reply_markup=get_catalog_keyboard(0, len(products), is_admin),
            )

    except Exception as e:
        await message.answer(catalog_service.config.error_text.format(error=str(e)))


@catalog_router.callback_query(lambda c: c.data.startswith("catalog_"))
async def process_catalog_navigation(callback: CallbackQuery, bot: Bot) -> None:
    parts = callback.data.split("_")

    if len(parts) != 3:
        raise ValueError("Invalid callback data format")

    action, current_index = parts[1], int(parts[2])

    if action in ["prev", "next"]:
        await handle_navigation(callback, bot, action, current_index)
    elif action == "delete":
        await handle_delete(callback, bot, current_index)
    elif action == "edit":
        await handle_edit(callback, bot, current_index)


async def handle_navigation(
    callback: CallbackQuery, bot: Bot, action: str, current_index: int
) -> None:
    try:
        products = await catalog_service.get_products()

        if not products:
            await callback.message.edit_text(catalog_service.config.no_products_text)
            await callback.answer()
            return

        # Calculate new index
        new_index = max(
            0,
            min(
                current_index
                + (-1 if action == "prev" else 1 if action == "next" else 0),
                len(products) - 1,
            ),
        )

        product = products[new_index]
        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.PRODUCT,
            args=ProductCaptionArgs(product=product),
        )
        is_admin = await IsAdmin()(callback)
        keyboard = get_catalog_keyboard(new_index, len(products), is_admin)

        if image_file := await catalog_service.get_product_image(product.id, product):
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

        await callback.answer()

    except Exception as e:
        await callback.message.edit_text(
            catalog_service.config.error_text.format(error=str(e))
        )
        await callback.answer()


async def handle_delete(callback: CallbackQuery, bot: Bot, current_index: int):
    try:
        products = await catalog_service.get_products()

        if not products or current_index >= len(products):
            await callback.answer(catalog_service.config.no_products_text)
            return

        product = products[current_index]
        delete_caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.DELETE,
            args=DeleteCaptionArgs(product_name=product.name),
        )
        keyboard = get_confirm_delete_keyboard(product.id)

        await callback.message.edit_caption(
            caption=delete_caption,
            reply_markup=keyboard,
        )
        await callback.answer()

    except Exception as e:
        await callback.message.edit_text(
            catalog_service.config.error_text.format(error=str(e))
        )
        await callback.answer()


@catalog_router.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    try:
        is_delete = await catalog_service.delete_product(product_id)
        if is_delete:
            caption = catalog_service.config.delete_success.format(
                name=html.bold(product_id)
            )
            await callback.message.edit_caption(caption=caption)

    except Exception as e:
        await callback.answer(catalog_service.config.error_text.format(error=str(e)))


async def handle_edit(callback: CallbackQuery, bot: Bot, current_index: int):
    pass


@catalog_router.message(Command("addproduct"), IsAdmin())
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
