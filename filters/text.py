from typing import Optional, Union, List
from aiogram.filters import BaseFilter
from aiogram.types import Message


class TextFilter(BaseFilter):
    def __init__(
        self,
        equals: Optional[Union[str, List[str]]] = None,
        contains: Optional[Union[str, List[str]]] = None,
        startswith: Optional[str] = None,
        endswith: Optional[str] = None,
        ignore_case: bool = False,
        strip: bool = True,
    ):
        """
        Фильтр для текстовых сообщений с расширенными возможностями проверки

        :param equals: Проверка на точное совпадение (строка или список строк)
        :param contains: Проверка на содержание подстроки (строка или список строк)
        :param startswith: Проверка начала строки
        :param endswith: Проверка конца строки
        :param ignore_case: Игнорировать регистр
        :param strip: Удалять пробелы по краям перед проверкой
        """
        self.equals = equals
        self.contains = contains
        self.startswith = startswith
        self.endswith = endswith
        self.ignore_case = ignore_case
        self.strip = strip

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        text = message.text.strip() if self.strip else message.text

        if self.ignore_case:
            text = text.lower()

        
        if self.equals is not None:
            if isinstance(self.equals, str):
                compare = self.equals.lower() if self.ignore_case else self.equals
                if self.strip:
                    compare = compare.strip()
                return text == compare
            elif isinstance(self.equals, list):
                compares = [
                    item.lower() if self.ignore_case else item for item in self.equals
                ]
                if self.strip:
                    compares = [item.strip() for item in compares]
                return text in compares

        
        if self.contains is not None:
            if isinstance(self.contains, str):
                compare = self.contains.lower() if self.ignore_case else self.contains
                return compare in text
            elif isinstance(self.contains, list):
                compares = [
                    item.lower() if self.ignore_case else item for item in self.contains
                ]
                return any(compare in text for compare in compares)

    
        if self.startswith is not None:
            compare = self.startswith.lower() if self.ignore_case else self.startswith
            return text.startswith(compare)

        
        if self.endswith is not None:
            compare = self.endswith.lower() if self.ignore_case else self.endswith
            return text.endswith(compare)

        return False
