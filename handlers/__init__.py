from .catalog import catalog_router
from .handle_router import HandleRouters
from .initial import initial_router
from .messages import message_router
from .product_add import product_add_router
from .product_delete import product_delete_router
from .product_edit import product_edit_router

catalog_router.include_routers(
    product_edit_router, product_add_router, product_delete_router
)

__routers__ = HandleRouters(
    routers=(
        initial_router,
        catalog_router,
        message_router,
    )
)
