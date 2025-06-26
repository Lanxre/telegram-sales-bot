from aiogram import Dispatcher

from handlers import __routers__


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    __routers__.register_routes(dispatcher)
    return dispatcher
