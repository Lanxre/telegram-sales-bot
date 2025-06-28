from typing import Any, Dict, Generic, Type, TypeVar

from aiogram.fsm.context import FSMContext
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StateToModel(Generic[T]):
    """Converts Aiogram FSM state data into a Pydantic model."""

    @staticmethod
    async def from_state(state_data: Dict[str, Any], model: Type[T]) -> T:
        return model(**state_data)

    @staticmethod
    async def to_state(model: T, exclude_unset: bool = True) -> Dict[str, Any]:
        return model.model_dump(exclude_unset=exclude_unset)

    @staticmethod
    async def from_context(context: FSMContext, model: Type[T]) -> T:
        """Directly converts the current FSM state into a model."""
        state_data = await context.get_data()
        return await StateToModel.from_state(state_data, model)
