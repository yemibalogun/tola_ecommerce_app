from flask import current_app, g
from flask_caching import Cache
from typing import List
from app.repositories.product_repo import ProductRepository  # ✅ import here
from app.models.product import Product

cache = Cache(config={
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300
})

@cache.cached(timeout=600, key_prefix="featured_products")
def get_featured_products() -> List[Product]:
    """
    Cached wrapper around ProductRepository.get_featured()
    """

    tenant_id = getattr(g, "tenant_id", None)
    if not tenant_id:
        current_app.logger.warning("No tenant_id found in request context")
        return []

    try:
        # Pass tenant_id because repository requires it
        products: List[Product] = ProductRepository.get_featured(tenant_id=tenant_id)
        return products or []

    except Exception as exc:
        current_app.logger.error("Failed to fetch featured products", exc_info=exc)
        return []
