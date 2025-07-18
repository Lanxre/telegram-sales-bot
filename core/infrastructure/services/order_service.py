from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import Order
from core.infrastructure.repositories import OrderRepository, ProductRepository
from core.internal.enums import OrderStatus
from core.internal.models import OrderCreate, OrderUpdate
from core.internal.types import ShopCardContent
from logger import LoggerBuilder
from utils import StringBuilder

logger = LoggerBuilder("OrderService - Service").add_stream_handler().build()


@dataclass(frozen=True)
class OrderDisplayFormatter:
    no_exist: str = "📦 У вас пока нет заказов"

    error: str = "❌ Ошибка при оформлении заказа"
    error_address: str = "❌ Ошибка при обработке адреса"
    error_note: str = "❌ Ошибка при обработке комментария"

    input_address: str = (
        "🏠 Теперь введите адрес доставки:\n(Укажите город, улицу, дом и квартиру)"
    )

    order_received = "Поступившие заказы на обработку:"
    order_status_change = "Статус заказа изменён"

    async def get_text_confirm_order(self, order: Order) -> str:
        return (
            f"✅ Заказ #{order.id} успешно оформлен!\n\n"
            f"Статус: {order.status.value}\n"
            f"Сумма: {order.total_price} $\n"
            f"Адрес: {order.delivery_address or 'не указан'}\n\n"
            f"Мы свяжемся с вами для уточнения деталей."
        )

    async def get_text_orders(self, orders: List[Order]) -> str:
        response = StringBuilder("📦 Ваши заказы:")
        for order in orders:
            response.append("\n\n")
            response.append(
                f"🆔 #{order.id} - {order.status.value}\n"
                f"💳 {order.total_price} $ - {order.created_at.strftime('%d.%m.%Y')}\n"
                f"🏠 {order.delivery_address or 'Адрес не указан'}\n"
                f"📊 - {order.status.value}"
            )
        return response.to_string()

    async def get_items_text(self, items: List[ShopCardContent]) -> str:
        items_text = "\n".join(
            f"{item.name} - {item.quantity} × {item.price} $" for item in items
        )
        return items_text

    async def get_text_for_confirm(
        self,
        items_text: str,
        total_price: float,
        address: str,
        order_note: Optional[str] = "Не указан",
    ) -> str:
        return (
            f"📦 Подтвердите заказ:\n\n"
            f"🛒 Состав заказа:\n{items_text}\n\n"
            f"💳 Итого: {total_price} $\n\n"
            f"🏠 Адрес доставки: {address}\n"
            f"📝 Комментарий: {order_note}"
        )

    async def get_text_order_price(self, price: float) -> str:
        return (
            f"💳 Оформление заказа на сумму: {price} $\n\n"
            "📝 Введите комментарий к заказу (например, пожелания по доставке):\n"
            "Или нажмите /skip чтобы пропустить"
        )

    async def get_text_order(self, order: Order) -> str:
        product_text = StringBuilder()
        for product_order, product in zip(order.order_products, order.products):
            product_text.append("\n")
            product_text.append(
                f"{product.name} - {product.price} × {product_order.product_quantity} = {product.price * product_order.product_quantity}$"
            )

        return (
            f"✅ Заказ #{order.id} !\n\n"
            f"Пользователь @{order.user.username}\n"
            f"📦 Статус: {order.status.value}\n"
            f"💳 Сумма: {order.total_price} $\n"
            f"🏠 Адрес: {order.delivery_address or 'не указан'}\n"
            f"📝 Комментарий: {order.order_note if order.order_note else 'не оставлен'}\n\n"
            f"🛒 Предметы: \n{product_text}\n"
            f"Общее кол-во: {order.total_count}"
        )


class OrderService:
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager
        self._display_formatter = OrderDisplayFormatter()

    @property
    def db_manager(self) -> DatabaseManager:
        return self._db_manager

    @property
    def formatter(self) -> OrderDisplayFormatter:
        return self._display_formatter

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self.db_manager.get_db_session() as session:
            try:
                yield session
            except SQLAlchemyError:
                raise
            except Exception:
                raise

    async def create_order(self, order_data: OrderCreate) -> Order:
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)
            products = [await product_repo.get(p[0].id) for p in order_data.products]
            order = Order(
                user_id=order_data.user_id,
                total_price=order_data.total_price,
                total_count=order_data.total_count,
                delivery_address=order_data.delivery_address,
                order_note=order_data.order_note,
                status=order_data.status,
                products=products,
            )

            session.add(order)

            for order_product in order.order_products:
                for product, quantity in order_data.products:
                    if product.id == order_product.product_id:
                        order_product.product_quantity = quantity
                        break

            await session.commit()
            return order

    async def get_order(self, order_id: int) -> Optional[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.get_with_products(order_id)

    async def get_user_orders(self, user_id: int) -> List[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.get_by_user(user_id)

    async def get_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.get_all_orders_with_products(
                skip=skip, limit=limit, filters=filters, order_by=order_by
            )

    async def cancel_order(self, order_id: int) -> bool:
        await self.update_order(order_id, OrderUpdate(status=OrderStatus.PENDING))

    async def update_order(
        self, order_id: int, update_data: OrderUpdate
    ) -> Optional[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.update(order_id, update_data)

    async def update_order_status(self, order_id: int, status: OrderStatus):
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.update_status(order_id, status)

    async def get_text_orders(self, orders: List[Order]) -> str:
        return await self._display_formatter.get_text_orders(orders)

    async def get_text_confirm_order(self, order: Order) -> str:
        return await self._display_formatter.get_text_confirm_order(order)

    async def get_text_for_confirm(
        self,
        items: List[ShopCardContent],
        total_price: float,
        address: str,
        order_note: Optional[str] = "Не указан",
    ) -> str:
        items_text = await self._display_formatter.get_items_text(items)

        return await self._display_formatter.get_text_for_confirm(
            items_text, total_price, address, order_note
        )

    async def get_text_order_price(self, price: float) -> str:
        return await self._display_formatter.get_text_order_price(price)

    async def get_text_order(self, order: Order) -> str:
        return await self.formatter.get_text_order(order)
