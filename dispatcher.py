from typing import Any, Dict

from aiogram import Dispatcher

from core.infrastructure import admin_config, db_manager
from handlers import __routers__
from middleware import AdminMiddleware, ServiceMiddleware
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore



def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}/LC_MESSAGES",
        )
    )

    dispatcher.update.middleware(ServiceMiddleware(db_manager, admin_config))
    dispatcher.update.middleware(AdminMiddleware(admin_config))
    i18n_middleware.setup(dispatcher)

    dispatcher["is_admin"] = get_is_admin

    __routers__.register_routes(dispatcher)
    return dispatcher


def get_is_admin(data: Dict[str, Any]) -> bool:
    return data.get("is_admin", False)
