from typing import List, Optional, Any

from pydantic import BaseModel


class PaginationData(BaseModel):
    text: str
    callback_name: str
    items: Optional[List[Any]] = None
    page: Optional[int] = 0
    page_size: Optional[int] = 10
