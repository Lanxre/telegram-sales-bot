from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from core.infrastructure.services import CatalogService, ShopCardService
from core.internal.models import ShopCardItemCreate, ShopCardItemUpdate
from keyboards import get_shop_card_keyboard
from logger import LoggerBuilder

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
    if success:
        await message.answer("🛒 Корзина очищена")
    else:
        await message.answer("🛒 Корзина уже пуста")


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_add_"))
async def handle_add_to_cart(
    callback: CallbackQuery, shop_card_service: ShopCardService
):
    try:
        product_id = int(callback.data.split("_")[-1])
        await shop_card_service.add_to_card(
            user_id=callback.from_user.id,
            item_data=ShopCardItemCreate(product_id=product_id, quantity=1),
        )
        await callback.answer("✅ Товар добавлен в корзину.", show_alert=True)
    except Exception:
        await callback.answer("❌ Не удалось добавить товар", show_alert=True)


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_delete_item_"))
async def delete_from_shopcard(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    try:
        product_id = int(callback.data.split("_")[-1])
        success = await shop_card_service.remove_from_card(
            callback.from_user.id, product_id
        )
        cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
        product = await catalog_service.get_product(cart_contents[0].product_id)
        image_file = await catalog_service.get_product_image(product_id, product)
        total_text_res = await shop_card_service.get_total_caption(cart_contents)
        keyboard = get_shop_card_keyboard(0, product.id, len(cart_contents))

        if success and image_file:
            await callback.answer("✅ Товар удален из корзины.", show_alert=True)
            await bot.edit_message_media(
                media=InputMediaPhoto(
                    media=image_file,
                    caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
                ),
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard,
            )
        elif success:
            await callback.answer("✅ Товар удален из корзины.", show_alert=True)
            await bot.edit_message_media(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
                reply_markup=keyboard,
            )
        else:
            await callback.answer("🛒 Корзина уже пуста")

    except Exception:
        await callback.answer("❌ Не удалось удалить из корзины.", show_alert=True)


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_item_inc_"))
async def shopcard_item_inc(
    callback: CallbackQuery, bot: Bot, shop_card_service: ShopCardService
):
    try:
        current_index = int(callback.data.split("_")[3])
        product_id = int(callback.data.split("_")[-1])
        await shop_card_service.add_to_card(
            user_id=callback.from_user.id,
            item_data=ShopCardItemCreate(product_id=product_id, quantity=1),
        )

        cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
        current_item = next(
            (item for item in cart_contents if item.product_id == product_id), None
        )
        total_text_res = await shop_card_service.get_total_caption(cart_contents)
        keyboard = get_shop_card_keyboard(current_index, product_id, len(cart_contents))

        await callback.answer("✅ Кол-во увеличено")
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=f"Текущий товар: {current_item.name}\n\n{total_text_res}",
            reply_markup=keyboard,
        )
    except Exception:
        await callback.answer("❌ Не удалось увеличить.", show_alert=True)


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_item_dec_"))
async def shopcard_item_dec(
    callback: CallbackQuery, bot: Bot, shop_card_service: ShopCardService
):
    try:
        current_index = int(callback.data.split("_")[3])
        product_id = int(callback.data.split("_")[-1])
        user_id = callback.from_user.id

        cart_contents = await shop_card_service.get_card_contents(user_id)

        current_item = next(
            (item for item in cart_contents if item.product_id == product_id), None
        )

        if not current_item:
            await callback.answer("❌ Товар не найден в корзине", show_alert=True)
            return

        if current_item.quantity <= 1:
            success = await shop_card_service.remove_from_card(user_id, product_id)

            if not success:
                await callback.answer("❌ Ошибка при удалении", show_alert=True)
                return

            cart_contents = await shop_card_service.get_card_contents(user_id)

            if not cart_contents:
                await callback.answer("✅ Товар удален (корзина пуста)")
                await bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )
                return

            total_text_res = await shop_card_service.get_total_caption(cart_contents)
            keyboard = get_shop_card_keyboard(
                0, cart_contents[0].product_id, len(cart_contents)
            )

            await callback.answer("✅ Товар удален")
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=f"Текущий товар: {cart_contents[0].name}\n\n{total_text_res}",
                reply_markup=keyboard,
            )
        else:
            await shop_card_service.update_card_item(
                item_id=current_item.id,
                update_data=ShopCardItemUpdate(quantity=current_item.quantity - 1),
            )

            cart_contents = await shop_card_service.get_card_contents(user_id)
            total_text_res = await shop_card_service.get_total_caption(cart_contents)
            keyboard = get_shop_card_keyboard(
                current_index, product_id, len(cart_contents)
            )

            await callback.answer("✅ Кол-во уменьшено")
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=f"Текущий товар: {current_item.name}\n\n{total_text_res}",
                reply_markup=keyboard,
            )

    except Exception:
        await callback.answer("❌ Ошибка при уменьшении", show_alert=True)


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_item_prev_"))
async def handle_prev_item(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    try:
        current_index = int(callback.data.split("_")[3])
        product_id = int(callback.data.split("_")[4])

        cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
        product = await catalog_service.get_product(
            cart_contents[current_index - 1].product_id
        )
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
                if item.product_id == product_id
            ),
            0,
        )

        new_pos = (current_pos - 1) % len(cart_contents)
        new_product = cart_contents[new_pos]

        total_text_res = await shop_card_service.get_total_caption(cart_contents)
        keyboard = get_shop_card_keyboard(
            current_index=new_pos,
            product_id=new_product.product_id,
            total_products=len(cart_contents),
        )

        if image_file := await catalog_service.get_product_image(product.id, product):
            await bot.edit_message_media(
                media=InputMediaPhoto(
                    media=image_file,
                    caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
                ),
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard,
            )

        else:
            await bot.edit_message_media(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
                reply_markup=keyboard,
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Previous item error: {e}", exc_info=True)
        await callback.answer("❌ Ошибка навигации", show_alert=True)


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_item_next_"))
async def handle_next_item(
    callback: CallbackQuery,
    bot: Bot,
    shop_card_service: ShopCardService,
    catalog_service: CatalogService,
):
    try:
        current_index = int(callback.data.split("_")[3])
        product_id = int(callback.data.split("_")[4])

        cart_contents = await shop_card_service.get_card_contents(callback.from_user.id)
        product = await catalog_service.get_product(
            cart_contents[current_index + 1].product_id
        )

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
                if item.product_id == product_id
            ),
            0,
        )

        new_pos = (current_pos + 1) % len(cart_contents)
        new_product = cart_contents[new_pos]

        total_text_res = await shop_card_service.get_total_caption(cart_contents)
        keyboard = get_shop_card_keyboard(
            current_index=new_pos,
            product_id=new_product.product_id,
            total_products=len(cart_contents),
        )

        if image_file := await catalog_service.get_product_image(product.id, product):
            await bot.edit_message_media(
                media=InputMediaPhoto(
                    media=image_file,
                    caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
                ),
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard,
            )

        else:
            await bot.edit_message_media(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=f"Текущий товар: {product.name}\n\n{total_text_res}",
                reply_markup=keyboard,
            )
        await callback.answer()

    except Exception:
        await callback.answer("❌ Ошибка навигации", show_alert=True)
