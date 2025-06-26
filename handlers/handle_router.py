from dataclasses import dataclass

from aiogram import Dispatcher


@dataclass(frozen=True)
class HandleRouters:
    routers: tuple

    def register_routes(self, dp: Dispatcher):
        for router in self.routers:
            dp.include_router(router)
