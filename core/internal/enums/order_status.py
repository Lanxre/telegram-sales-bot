from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "Ожидается"
    PROCESSING = "В Процессе"
    SHIPPED = "В Обработке"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"
