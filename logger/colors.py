from typing import Dict, TypedDict


class ColorCodes(TypedDict):
    time: str
    name: str
    level: Dict[int, str]
    message: str
    reset: str