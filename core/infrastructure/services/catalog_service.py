from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, TypedDict

from aiogram import html
from aiogram.types import BufferedInputFile

from core.infrastructure.database.models import Product
from core.internal.models import ProductUpdate
from logger import LoggerBuilder
from utils import ImageSelector

from .shop_service import ShopService

logger = LoggerBuilder("Catalog - Service").add_stream_handler().build()


class CaptionStrategyType(Enum):
    """Enum for caption strategy types"""

    PRODUCT = auto()
    DELETE = auto()
    EDIT = auto()


class CallbackAction(Enum):
    """Enum for callback actions"""

    PREV = auto()
    NEXT = auto()
    DELETE = auto()
    EDIT = auto()


class ProductCaptionArgs(TypedDict):
    """Type definition for product caption kwargs"""

    product: Product


class DeleteCaptionArgs(TypedDict):
    """Type definition for delete caption kwargs"""

    product_name: str


class ErrorCaptionArg(TypedDict):
    error: Exception


@dataclass(frozen=True)
class ProductDisplayFormatter:
    """Configuration for product display formatting"""

    name_format: str = "Название: {name}\n\n"
    description_format: str = "Описание: {description}\n\n"
    price_format: str = "Стоимость: {price}$"
    no_description_text: str = "Нет описания"
    no_products_text: str = "Нет предметов для продажи"
    error_text: str = "Ошибка в обработке предмета: {error}"
    delete_confirm: str = "Вы уверены, что хотите удалить: {name}?"
    delete_success: str = "Предмет был удален из каталога"
    delete_cancel: str = "Удаление отменено!"

    edit_name_prompt: str = "Пожалуйста, введите новое название предмета (или 'skip' для сохранения текущего)."
    edit_description_prompt: str = "Пожалуйста, введите новое описание предмета (или 'skip' для сохранения текущего)."
    edit_price_prompt: str = "Пожалуйста, введите новую стоимость предмета (например, 19.99, или 'skip' для сохранения текущей)."
    edit_image_prompt: str = "Пожалуйста, отправьте новое изображение предмета (или 'skip' для сохранения текущего)."
    edit_success: str = "Предмет '{name}' успешно обновлён (ID: {id}, Price: {price}$)"
    edit_cansel: str = ""
    edit_invalid_price: str = "Введите корректную цену (например, 19.99)."


class CaptionStrategy(ABC):
    """Abstract base class for caption building strategies"""

    def __init__(self, config: ProductDisplayFormatter):
        self.config = config

    @abstractmethod
    def build(self, args) -> str:
        """Build the caption based on provided typed arguments"""
        pass

    @abstractmethod
    def build_error(self, args) -> str:
        pass


class ProductCaptionStrategy(CaptionStrategy):
    """Strategy for building product display captions"""

    def build(self, args: ProductCaptionArgs) -> str:
        product = args.get("product")
        if not product:
            raise ValueError("Product is required for product caption")
        return (
            self.config.name_format.format(name=html.bold(product.name))
            + self.config.description_format.format(
                description=html.italic(
                    product.description or self.config.no_description_text
                )
            )
            + self.config.price_format.format(price=product.price)
        )

    def build_error(self, args):
        return super().build_error(args)


class DeleteCaptionStrategy(CaptionStrategy):
    """Strategy for building delete confirmation captions"""

    def build(self, args: DeleteCaptionArgs) -> str:
        product_name = args.get("product_name")
        if not product_name:
            raise ValueError("Product name is required for delete caption")
        return self.config.delete_confirm.format(name=html.bold(product_name))
    
    def build_error(self, args):
        return super().build_error(args)


class EditCaptionStrategy(CaptionStrategy):
    """Strategy for building edit confirmation captions"""

    def build(self, args: ProductCaptionArgs) -> str:
        product = args.get("product")

        if not product:
            raise ValueError("Product is required for product caption")

        return self.config.edit_success.format(
            name=html.bold(product.name),
            id=html.bold(product.id),
            price=html.bold(product.price),
        )

    def build_error(self, args: ErrorCaptionArg) -> str:
        error = args.get("error")
        return self.config.error_text.format(error=html.bold(str(error)))


class CatalogService:
    """Service layer for catalog operations"""

    def __init__(self, shop_service: ShopService):
        self.shop_service = shop_service
        self.config = ProductDisplayFormatter()
        self.caption_strategies: Dict[CaptionStrategyType, CaptionStrategy] = {
            CaptionStrategyType.PRODUCT: ProductCaptionStrategy(self.config),
            CaptionStrategyType.DELETE: DeleteCaptionStrategy(self.config),
            CaptionStrategyType.EDIT: EditCaptionStrategy(self.config),
        }

    async def get_products(self) -> List[Product]:
        """Get all products with validation"""
        products = await self.shop_service.get_all_products()

        if not isinstance(products, list):
            raise ValueError("Invalid products data received")

        return products

    async def delete_product(self, product_id: int) -> bool:
        is_delete = await self.shop_service.delete_product(product_id)
        return is_delete
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        updated_product = await self.shop_service.update_product(product_id, product_data)
        return updated_product

    async def get_product_image(
        self, product_id: int, product: Product
    ) -> BufferedInputFile:
        """Get product image file"""
        if not product.image:
            return None

        return await ImageSelector.get_image_file(
            product.image, f"product_{product_id}.jpg"
        )

    def build_caption(self, strategy_type: CaptionStrategyType, args) -> str:
        """Build caption using the specified strategy and typed args"""
        strategy = self.caption_strategies.get(strategy_type)
        if not strategy:
            raise ValueError(f"Unknown caption strategy: {strategy_type}")
        return strategy.build(args)

    def build_caption_error(self, strategy_type: CaptionStrategyType, args) -> str:
        """Build caption using the specified strategy and typed args"""
        strategy = self.caption_strategies.get(strategy_type)
        if not strategy:
            raise ValueError(f"Unknown caption strategy: {strategy_type}")
        return strategy.build_error(args)
