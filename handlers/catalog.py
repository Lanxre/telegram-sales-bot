from aiogram import Bot, Router, html
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from core.infrastructure.services import (
    CaptionStrategyType,
    CatalogService,
    DeleteCaptionArgs,
    ProductCaptionArgs,
)
from core.internal.enums import CallbackAction, CallbackPrefixes
from keyboards import (
    get_catalog_keyboard,
    get_confirm_delete_keyboard,
    get_edit_keyboard,
)

catalog_router = Router()


@catalog_router.message(Command("catalog"))
async def command_catalog(
    message: Message, catalog_service: CatalogService, is_admin: bool
) -> None:
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

        if image_file := await catalog_service.get_product_image(product.id, product):
            await message.answer_photo(
                photo=image_file,
                caption=caption,
                reply_markup=get_catalog_keyboard(0, product.id, len(products), is_admin),
            )
        else:
            await message.answer(
                text=caption,
                reply_markup=get_catalog_keyboard(0, product.id, len(products), is_admin),
            )

    except Exception as e:
        await message.answer(catalog_service.config.error_text.format(error=str(e)))


@catalog_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.CATALOG_INIT))
async def process_catalog_navigation(
    callback: CallbackQuery, bot: Bot, catalog_service: CatalogService, is_admin: bool
) -> None:
    parts = callback.data.split("_")

    if len(parts) != 3:
        raise ValueError("Invalid callback data format")

    try:
        action = CallbackAction[parts[1].upper()]
        current_index = int(parts[2])
    except KeyError:
        raise ValueError(f"Unknown callback action: {parts[1]}")

    if action == CallbackAction.PREV or action == CallbackAction.NEXT:
        await handle_navigation(
            callback, bot, action, current_index, catalog_service, is_admin
        )
    elif action == CallbackAction.DELETE:
        await handle_delete(callback, current_index, catalog_service)
    elif action == CallbackAction.EDIT:
        await handle_edit(callback, current_index, catalog_service)


async def handle_navigation(
    callback: CallbackQuery,
    bot: Bot,
    action: str,
    current_index: int,
    catalog_service: CatalogService,
    is_admin: bool,
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
                + (
                    -1
                    if action == CallbackAction.PREV
                    else 1
                    if action == CallbackAction.NEXT
                    else 0
                ),
                len(products) - 1,
            ),
        )

        product = products[new_index]
        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.PRODUCT,
            args=ProductCaptionArgs(product=product),
        )

        keyboard = get_catalog_keyboard(new_index, product.id, len(products), is_admin)

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


async def handle_delete(
    callback: CallbackQuery, current_index: int, catalog_service: CatalogService
):
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


async def handle_edit(
    callback: CallbackQuery, current_index: int, catalog_service: CatalogService
):
    try:
        products = await catalog_service.get_products()

        if not products or current_index >= len(products):
            await callback.answer(catalog_service.config.no_products_text)
            return

        product = products[current_index]
        keyboard = get_edit_keyboard(product.id, current_index)

        await callback.message.edit_caption(
            caption=f"Редактирование: {html.bold(product.name)}\n",
            reply_markup=keyboard,
        )

        await callback.answer()

    except Exception as e:
        await callback.message.edit_text(
            catalog_service.config.error_text.format(error=str(e))
        )
        await callback.answer()
