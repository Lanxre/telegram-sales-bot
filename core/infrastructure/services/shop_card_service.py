from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import ShopCard, ShopCardItem
from core.infrastructure.repositories import ShopCardItemRepository, ShopCardRepository
from core.internal.models import (
    ShopCardCreate,
    ShopCardItemCreate,
    ShopCardItemUpdate,
)
from core.internal.types import ShopCardContent, ShopCardTotal
from logger import LoggerBuilder

logger = LoggerBuilder("ShopCard - Service").add_stream_handler().build()


class ShopCardService:
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager

    @property
    def db_manager(self) -> DatabaseManager:
        return self._db_manager

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self.db_manager.get_db_session() as session:
            try:
                yield session
            except SQLAlchemyError:
                raise
            except Exception:
                raise

    async def get_or_create_card(self, user_id: int) -> ShopCard:
        """
        Получает или создает корзину для пользователя
        Args:
            user_id: ID пользователя
        Returns:
            ShopCard: Существующая или новая корзина
        """
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(ShopCardRepository, session)

            card = await repo.get_active_card(user_id)

            if not card:
                card = await repo.create(ShopCardCreate(user_id=user_id))
                logger.info(f"Created new shop card for user {user_id}")
            else:
                logger.debug(f"Found existing shop card for user {user_id}")

            return card

    async def add_to_card(
        self, user_id: int, item_data: ShopCardItemCreate
    ) -> ShopCardItem:
        """
        Добавляет товар в корзину пользователя
        Args:
            user_id: ID пользователя
            item_data: Данные для добавления товара
        Returns:
            ShopCardItem: Созданный или обновленный элемент корзины
        """
        async with self._get_session() as session:
            item_repo = self.db_manager.get_repo(ShopCardItemRepository, session)

            card = await self.get_or_create_card(user_id)
            
            existing_item = await item_repo.get_by_product(
                card.id, item_data.product_id
            )

            if existing_item:
                existing_item.quantity += item_data.quantity
                logger.info(
                    f"Updated quantity for product {item_data.product_id} in card {card.id}"
                )
            else:
                existing_item = await item_repo.create(
                    ShopCardItemCreate(
                        shop_card_id=card.id,
                        product_id=item_data.product_id,
                        quantity=item_data.quantity,
                    )
                )

                logger.info(
                    f"Added new product {item_data.product_id} to card {card.id}"
                )

            return existing_item

    async def get_card_contents(self, user_id: int) -> List[ShopCardContent]:
        """
        Получает содержимое корзины с информацией о товарах
        Args:
            user_id: ID пользователя
        Returns:
            List[Dict]: Список товаров в корзине с деталями
        """
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(ShopCardRepository, session)
            card = await repo.get_active_card_with_items(user_id)

            if not card:
                return []

            return [
                ShopCardContent(
                    id=item.id,
                    product_id=item.product_id,
                    name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                    total=item.product.price * item.quantity,
                )
                for item in card.items
            ]

    async def update_card_item(
        self, item_id: int, update_data: ShopCardItemUpdate
    ) -> Optional[ShopCardItem]:
        """
        Обновляет элемент корзины
        Args:
            item_id: ID элемента корзины
            update_data: Данные для обновления
        Returns:
            Optional[ShopCardItem]: Обновленный элемент или None если не найден
        """
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(ShopCardItemRepository, session)
            item = await repo.get(item_id)

            if not item:
                return None

            shop_cart_item_update_data = ShopCardItemUpdate()

            if update_data.quantity is not None:
                shop_cart_item_update_data.quantity = update_data.quantity

            if update_data.product_id is not None:
                shop_cart_item_update_data.product_id = update_data.product_id

            item = await repo.update(item_id, shop_cart_item_update_data)

            return item

    async def remove_from_card(self, user_id: int, product_id: int) -> bool:
        """
        Удаляет товар из корзины пользователя
        Args:
            user_id: ID пользователя
            product_id: ID товара
        Returns:
            bool: True если удаление успешно, False если элемент не найден
        """
        async with self._get_session() as session:
            card_repo = self.db_manager.get_repo(ShopCardRepository, session)
            item_repo = self.db_manager.get_repo(ShopCardItemRepository, session)

            card = await card_repo.get_active_card(user_id)
            if not card:
                return False

            item = await item_repo.get_by_product(card.id, product_id)
            if not item:
                return False

            await item_repo.delete(item.id)

            return True

    async def clear_card(self, user_id: int) -> bool:
        """
        Полностью очищает корзину пользователя
        Args:
            user_id: ID пользователя
        Returns:
            bool: True если корзина очищена, False если корзина не найдена
        """
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(ShopCardRepository, session)
            card = await repo.get_active_card_with_items(user_id)

            if not card:
                return False

            for item in card.items:
                await session.delete(item)

            await session.commit()
            logger.info(f"Cleared shop card for user {user_id}")
            return True

    async def get_card_total(self, user_id: int) -> ShopCardTotal:
        """
        Рассчитывает итоговую сумму корзины
        Args:
            user_id: ID пользователя
        Returns:
            Dict: Итоговая информация о корзине
        """
        contents = await self.get_card_contents(user_id)
        total = sum(item.total for item in contents)

        return ShopCardTotal(
            items_count=len(contents), 
            total_price=total, 
            items=contents
        )

    async def get_total_caption(self, cart_contents: List[ShopCardContent]) -> str:
        total = sum(item.total for item in cart_contents)
        response = ["🛒 Ваша корзина:"]

        for item in cart_contents:
            response.append(
                f"{item.name} - {item.quantity} × {item.price} $ = {item.total} $"
            )

        response.append(f"\n💳 Итого: {total} $")
        total_text_res = "\n".join(response)
        return total_text_res