from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.order import Order
from app.extensions.db import db


class OrderRepository(BaseRepository[Order]):
    model = Order

    @staticmethod
    def list_by_user(
        user_id: int,
        tenant_id: int
    ) -> List[Order]:
        if user_id <= 0 or tenant_id <= 0:
            return []

        return (
            Order.query
            .filter_by(user_id=user_id, tenant_id=tenant_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    @staticmethod
    def get_with_items(order_id: int) -> Optional[Order]:
        if order_id <= 0:
            return None

        return (
            Order.query
            .options(db.joinedload(Order.items))
            .filter_by(id=order_id)
            .first()
        )
