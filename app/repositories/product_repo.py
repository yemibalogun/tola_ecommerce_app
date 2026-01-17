from typing import List, Optional
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.product import Product


class ProductRepository(BaseRepository[Product]):
    model = Product

    @staticmethod
    def get_featured(
        tenant_id: int,
        limit: int = 12
    ) -> List[Product]:
        if tenant_id <= 0 or limit <= 0:
            return []

        return (
            Product.query
            .filter_by(tenant_id=tenant_id, is_active=True)
            .order_by(desc(Product.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_slug(
        slug: str,
        tenant_id: int
    ) -> Optional[Product]:
        if not slug or tenant_id <= 0:
            return None

        return (
            Product.query
            .filter_by(slug=slug, tenant_id=tenant_id, is_active=True)
            .first()
        )
