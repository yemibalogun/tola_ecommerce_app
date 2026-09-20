import re
from decimal import Decimal, InvalidOperation
from typing import Any

from flask import Flask, g, request, url_for
from markupsafe import Markup, escape

from app.utils.cart import cart_count

PLACEHOLDER = "images/placeholder.svg"


def media_url(path: str | None) -> str:
    """
    Resolve a stored upload path to a /static URL.
    Product images were historically stored as "admin/uploads/..." while the
    files live under static/uploads, so strip that prefix here, once.
    """
    if not path:
        return url_for("static", filename=PLACEHOLDER)

    if path.startswith(("http://", "https://", "/")):
        return path

    if path.startswith("admin/uploads/"):
        path = path[len("admin/"):]

    return url_for("static", filename=path)


def money(value: Any, symbol: str | None = None) -> str:
    """
    Format a price with the current store's currency symbol.
    """
    try:
        amount = Decimal(str(value or 0))
    except (InvalidOperation, ValueError):
        amount = Decimal("0")

    if symbol is None:
        tenant = getattr(g, "tenant", None)
        symbol = getattr(tenant, "currency_symbol", None) or "₦"

    return f"{symbol}{amount:,.2f}"


_HIGHLIGHT = re.compile(r"\*([^*]+)\*")


def highlight(text: str | None) -> Markup:
    """
    Render "Elevate Your *Audio* Journey" with the starred words in the
    accent gradient. Input is escaped first, so owner text can't inject HTML.
    """
    safe = str(escape(text or ""))
    return Markup(_HIGHLIGHT.sub(r'<span class="text-gradient">\1</span>', safe))


def plain(text: str | None) -> str:
    """Strip the *highlight* markers, e.g. for <title>."""
    return (text or "").replace("*", "")


def register_template_helpers(app: Flask) -> None:
    app.jinja_env.filters["money"] = money
    app.jinja_env.filters["highlight"] = highlight
    app.jinja_env.filters["plain"] = plain
    app.jinja_env.globals["media_url"] = media_url

    @app.context_processor
    def inject_store_helpers() -> dict[str, Any]:
        tenant = getattr(g, "tenant", None)
        in_store = request.blueprint == "store" or (
            tenant is not None and request.endpoint == "web.home"
        )

        def store_link(t: Any = None, external: bool = True) -> str:
            """Shareable URL for a store (defaults to the current one)."""
            t = t or tenant
            return url_for("store.home", store_slug=t.slug, _external=external)

        return {
            "store_link": store_link,
            "cart_count": cart_count(tenant.id) if (in_store and tenant) else 0,
        }
