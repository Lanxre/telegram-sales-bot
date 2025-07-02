from aiogram import Bot, Router, html
from aiogram.types import CallbackQuery, InputMediaPhoto

from core.infrastructure.services import (
    CaptionStrategyType,
    ProductCaptionArgs,
    CatalogService,
)
from filters import IsAdmin
from keyboards import (
    get_catalog_keyboard,
)

product_delete_router = Router()


@product_delete_router.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery, catalog_service: CatalogService):
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


@product_delete_router.callback_query(lambda c: c.data.startswith("cancel_delete_"))
async def cancel_delete(
    callback: CallbackQuery, bot: Bot, catalog_service: CatalogService
) -> None:
    try:
        product_id = int(callback.data.split("_")[2])
        products = await catalog_service.get_products()

        if not products:
            await callback.message.edit_text(catalog_service.config.no_products_text)
            await callback.answer()
            return

        current_index = next(
            (i for i, p in enumerate(products) if p.id == product_id), None
        )

        if current_index is None:
            await callback.answer(catalog_service.config.no_products_text)
            return

        product = products[current_index]

        caption = catalog_service.build_caption(
            strategy_type=CaptionStrategyType.PRODUCT,
            args=ProductCaptionArgs(product=product),
        )

        is_admin = await IsAdmin()(callback)
        keyboard = get_catalog_keyboard(current_index, len(products), is_admin)

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

        await callback.answer(catalog_service.config.delete_cancel)

    except Exception as e:
        await callback.message.edit_text(
            catalog_service.config.error_text.format(error=str(e))
        )
        await callback.answer()
