from typing import List
from app.repositories.base import BaseRepository
from app.models.order_item import OrderItem


class OrderItemRepository(BaseRepository[OrderItem]):
    model = OrderItem

    @staticmethod
    def list_by_order(order_id: int) -> List[OrderItem]:
        if order_id <= 0:
            return []

        return OrderItem.query.filter_by(order_id=order_id).all()
