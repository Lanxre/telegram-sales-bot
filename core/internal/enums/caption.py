from enum import Enum, auto


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
