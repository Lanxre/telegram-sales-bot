from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from core.infrastructure.services import CatalogService, ShopCardService
from core.internal.enums import CallbackPrefixes
from core.internal.types import CartCallbackData
from core.internal.models import ShopCardItemCreate, ShopCardItemUpdate
from keyboards import get_shop_card_keyboard
from logger import LoggerBuilder
from utils import handle_shopcard_errors

logger = LoggerBuilder("ShopCardRouter").add_stream_handler().build()

shop_card_router = Router()


@shop_card_router.message(Command("shopcard"))
async def command_shopcard(
    message: Message,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
) -> None:
    cart_contents = await shop_card_service.get_card_contents(message.from_user.id)

    if not cart_contents:
        await message.answer("🛒 Ваша корзина пуста")
        return

    product = await catalog_service.get_product(cart_contents[0].product_id)
    total_text_res = await shop_card_service.get_total_caption(cart_contents)
    keyboard = get_shop_card_keyboard(0, product.id, len(cart_contents))

    if image_file := await catalog_service.get_product_image(product.id, product):
        await message.answer_photo(
            photo=image_file,
            caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            text=f"Текущий товар: {product.name}\n\n{total_text_res}",
            reply_markup=keyboard,
        )


@shop_card_router.message(Command("clearcart"))
async def clear_cart_handler(message: Message, shop_card_service: ShopCardService):
    success = await shop_card_service.clear_card(message.from_user.id)
    await message.answer("🛒 Корзина очищена" if success else "🛒 Корзина уже пуста")


@shop_card_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.SHOPCARD_ADD))
@handle_shopcard_errors
async def handle_add_to_cart(
    callback: CallbackQuery, shop_card_service: ShopCardService
):
    product_id = CallbackPrefixes.last_index_after_prefix(
        callback.data, CallbackPrefixes.SHOPCARD_ADD
    )
    await shop_card_service.add_to_card(
        user_id=callback.from_user.id,
        item_data=ShopCardItemCreate(product_id=product_id, quantity=1),
    )
    await callback.answer("✅ Товар добавлен в корзину.", show_alert=True)


@shop_card_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.SHOPCARD_DELETE))
@handle_shopcard_errors
async def delete_from_shopcard(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    product_id = CallbackPrefixes.last_index_after_prefix(
        callback.data, CallbackPrefixes.SHOPCARD_DELETE
    )
    success = await shop_card_service.remove_from_card(
        callback.from_user.id, product_id
    )

    if not success:
        await callback.answer("❌ Товар не найден в корзине", show_alert=True)
        return

    cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)

    if not cart_contents:
        await callback.answer("✅ Корзина теперь пуста", show_alert=True)
        await bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        return

    await update_cart_message(
        bot,
        callback,
        cart_contents,
        0,
        cart_contents[0].product_id,
        catalog_service,
        shop_card_service,
    )
    await callback.answer("✅ Товар удален из корзины.")


@shop_card_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.SHOPCARD_ITEM_INCREMENT))
@handle_shopcard_errors
async def shopcard_item_inc(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    cb_data = CartCallbackData.parse(callback.data)
    if not cb_data:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    await shop_card_service.add_to_card(
        user_id=callback.from_user.id,
        item_data=ShopCardItemCreate(product_id=cb_data.product_id, quantity=1),
    )

    cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
    await update_cart_message(
        bot,
        callback,
        cart_contents,
        cb_data.current_index,
        cb_data.product_id,
        catalog_service,
        shop_card_service,
    )
    await callback.answer("✅ Кол-во увеличено")


@shop_card_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.SHOPCARD_ITEM_DECREMENT))
@handle_shopcard_errors
async def shopcard_item_dec(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    cb_data = CartCallbackData.parse(callback.data)
    if not cb_data:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
    current_item = next(
        (item for item in cart_contents if item.product_id == cb_data.product_id), None
    )

    if not current_item:
        await callback.answer("❌ Товар не найден в корзине", show_alert=True)
        return

    if current_item.quantity <= 1:
        await shop_card_service.remove_from_card(
            callback.from_user.id, cb_data.product_id
        )
        cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)

        if not cart_contents:
            await callback.answer("✅ Корзина теперь пуста", show_alert=True)
            await bot.delete_message(
                chat_id=callback.message.chat.id, message_id=callback.message.message_id
            )
            return

        await update_cart_message(
            bot,
            callback,
            cart_contents,
            0,
            cart_contents[0].product_id,
            catalog_service,
            shop_card_service,
        )
        await callback.answer("✅ Товар удален")
    else:
        await shop_card_service.update_card_item(
            item_id=current_item.id,
            update_data=ShopCardItemUpdate(quantity=current_item.quantity - 1),
        )
        await update_cart_message(
            bot,
            callback,
            cart_contents,
            cb_data.current_index,
            cb_data.product_id,
            catalog_service,
            shop_card_service,
        )
        await callback.answer("✅ Кол-во уменьшено")


@shop_card_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.SHOPCARD_ITEM_PREV))
@handle_shopcard_errors
async def handle_prev_item(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    cb_data = CartCallbackData.parse(callback.data)
    if not cb_data:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
    if not cart_contents:
        await callback.answer("🛒 Корзина пуста", show_alert=True)
        await bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        return

    current_pos = next(
        (
            i
            for i, item in enumerate(cart_contents)
            if item.product_id == cb_data.product_id
        ),
        0,
    )
    new_pos = (current_pos - 1) % len(cart_contents)
    new_product_id = cart_contents[new_pos].product_id

    await update_cart_message(
        bot,
        callback,
        cart_contents,
        new_pos,
        new_product_id,
        catalog_service,
        shop_card_service,
    )
    await callback.answer()


@shop_card_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.SHOPCARD_ITEM_NEXT))
@handle_shopcard_errors
async def handle_next_item(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    cb_data = CartCallbackData.parse(callback.data)
    if not cb_data:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
    if not cart_contents:
        await callback.answer("🛒 Корзина пуста", show_alert=True)
        await bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        return

    current_pos = next(
        (
            i
            for i, item in enumerate(cart_contents)
            if item.product_id == cb_data.product_id
        ),
        0,
    )
    new_pos = (current_pos + 1) % len(cart_contents)
    new_product_id = cart_contents[new_pos].product_id

    await update_cart_message(
        bot,
        callback,
        cart_contents,
        new_pos,
        new_product_id,
        catalog_service,
        shop_card_service,
    )
    await callback.answer()


async def update_cart_message(
    bot: Bot,
    callback: CallbackQuery,
    cart_contents: list,
    current_index: int,
    product_id: int,
    catalog_service: CatalogService,
    shop_card_service: ShopCardService,
) -> None:
    product = await catalog_service.get_product(product_id)
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return

    total_text = await shop_card_service.get_total_caption(cart_contents)
    keyboard = get_shop_card_keyboard(current_index, product_id, len(cart_contents))

    if image_file := await catalog_service.get_product_image(product_id, product):
        media = InputMediaPhoto(
            media=image_file, caption=f"Текущий товар: {product.name}\n\n{total_text}"
        )
        await bot.edit_message_media(
            media=media,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=keyboard,
        )
    else:
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=f"Текущий товар: {product.name}\n\n{total_text}",
            reply_markup=keyboard,
        )
