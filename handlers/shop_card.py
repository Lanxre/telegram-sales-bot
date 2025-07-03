from typing import List
from aiogram import Bot, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from core.infrastructure.services import CatalogService
from logger import LoggerBuilder

logger = LoggerBuilder("ShopCardRouter").add_stream_handler().build()

shop_card_router = Router()


@shop_card_router.message(Command("shopcard"))
async def command_catalog(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    shop_card = data.get("shop_card")

    if not shop_card:
        message.answer("Корзина пуста! Для покупки добавьте товар из каталога.")


@shop_card_router.callback_query(lambda c: c.data.startswith("shopcard_add_"))
async def answer_apeals_tag(
    callback: CallbackQuery, state: FSMContext, catalog_service: CatalogService
):
    try:
        state_data = await state.get_data()
        shop_card: List = state_data.get("shop_card", [])
        product_id = int(callback.data.split("_")[-1])
        
        product = await catalog_service.get_product(product_id)
        if not product:
            await callback.answer("Товар не найден")
            return
        
        updated_card = shop_card + [product]
        
        await state.update_data(shop_card=updated_card)
        await callback.answer(f"{product.name} добавлен в корзину")
        
        logger.info(f"Product {product_id} added to cart for user {callback.from_user.id}")
        
    except ValueError:
        await callback.answer("Ошибка: неверный ID товара")
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        await callback.answer("Произошла ошибка")
