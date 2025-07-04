from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.infrastructure.services import (
    CaptionStrategyType,
    CatalogService,
    ErrorCaptionArg,
    ProductCaptionArgs,
)
from core.internal.models import ProductUpdate
from utils import ImageSelector

from states import EditProduct

product_edit_router = Router()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_name_"))
async def proccess_edit_name(
    callback: CallbackQuery, state: FSMContext, catalog_service: CatalogService
):
    product_id = int(callback.data.split("_")[-1])
    await callback.message.answer(catalog_service.config.edit_name_prompt)
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_name)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_name)
async def process_edit_name(
    message: Message, state: FSMContext, catalog_service: CatalogService
):
    data = await state.get_data()
    product_id = data.get("product_id")

    user_message = message.text.strip()

    if user_message.lower() == "skip":
        await message.answer("Название не изменено")
        await state.clear()
        return

    try:
        product = await catalog_service.update_product(
            product_id=product_id, product_data=ProductUpdate(name=user_message)
        )

        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.EDIT,
            args=ProductCaptionArgs(product=product),
        )

        await message.answer(caption)

    except Exception as e:
        caption = catalog_service.build_caption_error(
            strategy_type=CaptionStrategyType.EDIT,
            args=ErrorCaptionArg(error=e),
        )
        await message.answer(caption)

    await state.clear()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_desc_"))
async def proccess_edit_descriprion(
    callback: CallbackQuery, state: FSMContext, catalog_service: CatalogService
):
    product_id = int(callback.data.split("_")[-1])
    await callback.message.answer(catalog_service.config.edit_description_prompt)
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_description)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_description)
async def process_edit_description(
    message: Message, state: FSMContext, catalog_service: CatalogService
):
    data = await state.get_data()
    product_id = data.get("product_id")
    user_message = message.text.strip()

    if user_message.lower() == "skip":
        await message.answer("Описание не изменено")
        await state.clear()
        return

    try:
        product = await catalog_service.update_product(
            product_id=product_id, product_data=ProductUpdate(description=user_message)
        )

        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.EDIT,
            args=ProductCaptionArgs(product=product),
        )

        await message.answer(caption)

    except Exception as e:
        caption = catalog_service.build_caption_error(
            strategy_type=CaptionStrategyType.EDIT,
            args=ErrorCaptionArg(error=e),
        )
        await message.answer(caption)

    await state.clear()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_price_"))
async def proccess_edit_price(
    callback: CallbackQuery, state: FSMContext, catalog_service: CatalogService
):
    product_id = int(callback.data.split("_")[-1])
    await callback.message.answer(catalog_service.config.edit_price_prompt)
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_price)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_price)
async def process_edit_price(
    message: Message, state: FSMContext, catalog_service: CatalogService
):
    data = await state.get_data()
    product_id = data.get("product_id")

    if message.text.strip().lower() == "skip":
        await message.answer("Цена не изменена")
        await state.clear()
        return

    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError("Цена должна быть положительной")

        product = await catalog_service.update_product(
            product_id=product_id, product_data=ProductUpdate(price=price)
        )

        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.EDIT,
            args=ProductCaptionArgs(product=product),
        )

        await message.answer(caption)
    except ValueError:
        await message.answer("Введите корректную цену (например: 19.99)")
        return

    except Exception as e:
        caption = catalog_service.build_caption_error(
            strategy_type=CaptionStrategyType.EDIT,
            args=ErrorCaptionArg(error=e),
        )
        await message.answer(caption)

    await state.clear()


@product_edit_router.callback_query(lambda c: c.data.startswith("edit_image_"))
async def proccess_edit_image(
    callback: CallbackQuery, state: FSMContext, catalog_service: CatalogService
):
    product_id = int(callback.data.split("_")[-1])
    await callback.message.answer(catalog_service.config.edit_image_prompt)
    await state.update_data(product_id=product_id)
    await state.set_state(EditProduct.waiting_for_image)
    await callback.answer()


@product_edit_router.message(EditProduct.waiting_for_image)
async def process_edit_image(
    message: Message, state: FSMContext, bot: Bot, catalog_service: CatalogService
):
    data = await state.get_data()
    product_id = data.get("product_id")

    if message.text and message.text.strip().lower() == "skip":
        await message.answer("Изображение не изменено")
        await state.clear()
        return

    if not message.photo:
        await message.answer("Пожалуйста, отправьте изображение или введите 'skip'")
        return

    try:
        image_bytes = await ImageSelector.get_image_bytes(message, bot)

        product = await catalog_service.update_product(
            product_id=product_id, product_data=ProductUpdate(image=image_bytes.read())
        )

        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.EDIT,
            args=ProductCaptionArgs(product=product),
        )

        await message.answer(caption)
    except Exception as e:
        caption = catalog_service.build_caption_error(
            strategy_type=CaptionStrategyType.EDIT,
            args=ErrorCaptionArg(error=e),
        )
        await message.answer(caption)

    await state.clear()
