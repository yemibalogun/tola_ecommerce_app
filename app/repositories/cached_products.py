from typing import List
from flask import current_app, g
from app.extensions.cache import cache
from app.repositories.product_repo import ProductRepository
from app.models.product import Product

@cache.cached(timeout=600, key_prefix='featured_products')
def get_featured_products() -> List[Product]:
    """
    Cached wrapper around ProductRepository.get_featured()

    - Avoids repeated DB hits for homepage
    - Safe to call from routes or services
    - Explicit return type helps static analysis
    """

    try:
        # 🔹 Use current tenant from request context or g
        tenant_id = getattr(g, "tenant_id", None)
        if not tenant_id:
            current_app.logger.warning("No tenant_id found in context")
            return []

        products: List[Product] = ProductRepository.get_featured(tenant_id=tenant_id)

        # Edge case: ensure empty list, never None
        return products or []

    except Exception as exc:
        current_app.logger.error(
            "Failed to fetch featured products",
            exc_info=exc
        )
        return []
