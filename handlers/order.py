from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.infrastructure.services import OrderService, ShopCardService
from core.internal.enums import OrderStatus
from core.internal.models import OrderCreate
from filters import TextFilter
from logger import LoggerBuilder
from states import OrderConfirm

logger = LoggerBuilder("OrderRouter").add_stream_handler().build()

order_router = Router()


@order_router.callback_query(F.data == "order_confirm")
async def start_order_process(
    callback: CallbackQuery, state: FSMContext, shop_card_service: ShopCardService
):
    try:
        cart_data = await shop_card_service.get_card_total(callback.from_user.id)

        if not cart_data.items_count:
            await callback.answer("🛒 Ваша корзина пуста", show_alert=True)
            return

        await state.set_data(
            {
                "cart_contents": cart_data.items,
                "total_price": cart_data.total_price,
            }
        )

        await state.set_state(OrderConfirm.waiting_for_order_note)

        await callback.message.answer(
            f"💳 Оформление заказа на сумму: {cart_data.total_price} ₽\n\n"
            "📝 Введите комментарий к заказу (например, пожелания по доставке):\n"
            "Или нажмите /skip чтобы пропустить",
            reply_markup=ReplyKeyboardRemove(),
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Order confirmation error: {e}", exc_info=True)
        await callback.message.answer("❌ Ошибка при оформлении заказа")
        await state.clear()


@order_router.message(
    OrderConfirm.waiting_for_order_note, ~TextFilter(equals="skip", ignore_case=True)
)
async def process_order_note(message: Message, state: FSMContext):
    try:
        if message.text != "/skip":
            await state.update_data(order_note=message.text)

        await state.set_state(OrderConfirm.waiting_for_address_delivery)
        await message.answer(
            "🏠 Теперь введите адрес доставки:\n(Укажите город, улицу, дом и квартиру)",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        await message.answer("❌ Ошибка при обработке комментария")
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
):
    try:
        state_data = await state.get_data()
        address = message.text.strip()

        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Подтвердить", callback_data="final_confirm")
        builder.button(text="❌ Отменить", callback_data="order_cancel")

        items_text = "\n".join(
            f"{item.name} - {item.quantity} × {item.price} $"
            for item in state_data["cart_contents"]
        )

        await message.answer(
            f"📦 Подтвердите заказ:\n\n"
            f"🛒 Состав заказа:\n{items_text}\n\n"
            f"💳 Итого: {state_data['total_price']} $\n\n"
            f"🏠 Адрес доставки: {address}\n"
            f"📝 Комментарий: {state_data.get('order_note', 'не указан')}",
            reply_markup=builder.as_markup(),
        )

    except Exception as e:
        logger.error(f"Order confirmation error: {e}", exc_info=True)
        await message.answer("❌ Ошибка при обработке адреса")
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

        await callback.message.edit_text(
            f"✅ Заказ #{order.id} успешно оформлен!\n\n"
            f"Статус: {order.status.value}\n"
            f"Сумма: {order.total_price} $\n"
            f"Адрес: {order.delivery_address or 'не указан'}\n\n"
            f"Мы свяжемся с вами для уточнения деталей."
        )

        await state.clear()

    except Exception:
        await callback.message.answer("❌ Ошибка при оформлении заказа")
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
        await message.answer("📦 У вас пока нет заказов")
        return

    response = ["📦 Ваши заказы:"]
    for order in orders:
        response.append(
            f"🆔 #{order.id} - {order.status.value}\n"
            f"💳 {order.total_price} ₽ - {order.created_at.strftime('%d.%m.%Y')}\n"
            f"🏠 {order.delivery_address or 'Адрес не указан'}"
        )

    await message.answer("\n\n".join(response))
