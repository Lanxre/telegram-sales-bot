from .initial import initial_router
from .catalog import catalog_router

from .handle_router import HandleRouters
__routers__ = HandleRouters(routers=(initial_router, catalog_router, ))