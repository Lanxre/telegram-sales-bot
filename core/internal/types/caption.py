from typing import TypedDict
from core.infrastructure.database.models import Product


class ProductCaptionArgs(TypedDict):
    """Type definition for product caption kwargs"""

    product: Product


class DeleteCaptionArgs(TypedDict):
    """Type definition for delete caption kwargs"""

    product_name: str


class ErrorCaptionArg(TypedDict):
    error: Exception
