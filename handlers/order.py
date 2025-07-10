from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)

from core.infrastructure.services import OrderService, ShopCardService
from core.internal.enums import OrderStatus
from core.internal.models import OrderCreate
from filters import TextFilter
from keyboards import get_order_confirm_keyboard
from logger import LoggerBuilder
from states import OrderConfirm

logger = LoggerBuilder("OrderRouter").add_stream_handler().build()

order_router = Router()


@order_router.callback_query(F.data == "order_confirm")
async def start_order_process(
    callback: CallbackQuery,
    state: FSMContext,
    shop_card_service: ShopCardService,
    order_service: OrderService,
):
    try:
        cart_data = await shop_card_service.get_card_total(callback.from_user.id)

        if not cart_data.items_count:
            await callback.answer("🛒 Ваша корзина пуста", show_alert=True)
            return

        await state.update_data(
            cart_contents=cart_data.items, total_price=cart_data.total_price
        )

        await state.set_state(OrderConfirm.waiting_for_order_note)
        text = await order_service.get_text_order_price(cart_data.total_price)
        await callback.message.answer(
            text,
            reply_markup=ReplyKeyboardRemove(),
        )
        await callback.answer()

    except Exception:
        await callback.message.answer(order_service.formatter.error)
        await state.clear()


@order_router.message(
    OrderConfirm.waiting_for_order_note, ~TextFilter(equals="skip", ignore_case=True)
)
async def process_order_note(
    message: Message, state: FSMContext, order_service: OrderService
):
    try:
        if message.text != "/skip":
            await state.update_data(order_note=message.text)

        await state.set_state(OrderConfirm.waiting_for_address_delivery)
        await message.answer(
            order_service.formatter.input_address,
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        await message.answer(order_service.formatter.error_note)
        await state.clear()


@order_router.message(
    OrderConfirm.waiting_for_order_note, TextFilter(equals="skip", ignore_case=True)
)
async def skip_order_note(message: Message, state: FSMContext):
    await state.update_data(order_note=None)
    await state.set_state(OrderConfirm.waiting_for_address_delivery)
    await message.answer(
        "🏠 Введите адрес доставки:", reply_markup=ReplyKeyboardRemove()
    )


@order_router.message(OrderConfirm.waiting_for_address_delivery)
async def process_delivery_address(
    message: Message,
    state: FSMContext,
    order_service: OrderService,
):
    try:
        state_data = await state.get_data()
        address = message.text.strip()

        await state.update_data(delivery_address=address)

        keyboard = get_order_confirm_keyboard()
        text_for_confirm = await order_service.get_text_for_confirm(
            items=state_data["cart_contents"],
            total_price=state_data["total_price"],
            address=address,
            order_note=state_data.get("order_note", "не указан"),
        )
        await message.answer(
            text_for_confirm,
            reply_markup=keyboard,
        )

    except Exception:
        await message.answer(order_service.formatter.error_address)
        await state.clear()


@order_router.callback_query(F.data == "final_confirm")
async def final_order_confirmation(
    callback: CallbackQuery,
    state: FSMContext,
    order_service: OrderService,
    shop_card_service: ShopCardService,
):
    try:
        state_data = await state.get_data()
        card_contents_total = await shop_card_service.get_card_total(
            callback.from_user.id
        )

        order = await order_service.create_order(
            OrderCreate(
                user_id=callback.from_user.id,
                total_count=card_contents_total.items_count,
                total_price=card_contents_total.total_price,
                status=OrderStatus.PENDING.value,
                products=[card_item.product for card_item in card_contents_total.items],
                delivery_address=state_data.get("delivery_address"),
                order_note=state_data.get("order_note"),
            )
        )

        if order:
            await shop_card_service.clear_card(callback.from_user.id)

        await callback.message.edit_text(order_service.get_text_confirm_order(order))

        await state.clear()

    except Exception:
        await callback.message.answer(order_service.formatter.error)
        await state.clear()


@order_router.callback_query(F.data == "order_cancel")
async def cancel_order_process(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Оформление заказа отменено\nВаша корзина сохранена для будущих покупок."
    )


@order_router.message(Command("myorders"))
async def show_user_orders(message: Message, order_service: OrderService):
    orders = await order_service.get_user_orders(message.from_user.id)

    if not orders:
        await message.answer(order_service.formatter.no_exist)
        return

    text_orders = await order_service.get_text_orders(orders)
    await message.answer(text_orders)
