from typing import Optional, List
from app.repositories.base import BaseRepository
from app.models.product_variant import ProductVariant


class ProductVariantRepository(BaseRepository[ProductVariant]):
    model = ProductVariant

    @staticmethod
    def get_by_sku(sku: str) -> Optional[ProductVariant]:
        if not sku:
            return None

        return ProductVariant.query.filter_by(sku=sku).first()

    @staticmethod
    def list_by_product(product_id: int) -> List[ProductVariant]:
        if product_id <= 0:
            return []

        return ProductVariant.query.filter_by(product_id=product_id).all()
