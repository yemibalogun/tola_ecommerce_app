# checkout_service.py
from decimal import Decimal
from typing import Dict, Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.extensions.db import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product_variant import ProductVariant

class CheckoutError(Exception):
    """Raised when checkout fails safely."""
    pass


class CheckoutService:
    """
    Handles checkout with strict atomicity:
    - Inventory is locked
    - Prices are snapshotted
    - Order + items + payment created in one transaction
    """

    @staticmethod
    def checkout(
        *,
        user_id: int,
        tenant_id: int,
        cart: Dict[int, int],  # {variant_id: quantity}
        payment_provider: str,
        payment_reference: str,
    ) -> Order:
        """
        Executes a full checkout atomically.

        Raises:
            CheckoutError: if anything fails
        """

        # ---- Basic validation (fail fast) ----
        if user_id <= 0 or tenant_id <= 0:
            raise CheckoutError("Invalid user or tenant")
        if not cart:
            raise CheckoutError("Cart is empty")

        session = db.session  # runtime scoped session

        try:
            total_amount = Decimal("0.00")
            locked_variants: Dict[int, ProductVariant] = {}

            # ---- INVENTORY LOCK PHASE ----
            for variant_id, quantity in cart.items():
                if quantity <= 0:
                    raise CheckoutError("Invalid quantity detected")

                # SELECT ... FOR UPDATE prevents race conditions
                variant: Optional[ProductVariant] = (
                    session.execute(
                        select(ProductVariant)
                        .where(
                            ProductVariant.id == variant_id,
                            ProductVariant.tenant_id == tenant_id,  # multi-tenant safety
                        )
                        .with_for_update()
                    )
                    .scalars()
                    .first()
                )

                if not variant:
                    raise CheckoutError(f"Variant {variant_id} not found")

                if variant.stock_quantity is None or int(variant.stock_quantity) < quantity:    # type: ignore  
                    raise CheckoutError(f"Insufficient stock for {variant.sku}")

                # Price resolution: variant override wins else product price
                if variant.price_override is not None:
                    unit_price = Decimal(float(variant.price_override)) # type: ignore
                else:
                    unit_price = Decimal(float(variant.product.price))

                total_amount += unit_price * quantity
                locked_variants[variant_id] = variant

            # ---- ORDER CREATION PHASE ----
            order = Order()
            order.user_id = user_id
            order.tenant_id = tenant_id
            order.status = "pending"
            order.total_amount = total_amount
            session.add(order)
            session.flush()  # ensures order.id exists

            # ---- ORDER ITEMS + STOCK DEDUCTION ----
            for variant_id, quantity in cart.items():
                variant = locked_variants[variant_id]

                if variant.price_override is not None:
                    unit_price = Decimal(float(variant.price_override)) # type: ignore
                else:
                    unit_price = Decimal(float(variant.product.price))

                item = OrderItem()
                item.order_id = order.id
                item.product_id = variant.product_id
                item.variant_id = variant.id
                item.quantity = quantity
                item.unit_price = unit_price

                session.add(item)

                # Deduct inventory safely (still locked)
                variant.stock_quantity -= quantity  # type: ignore

            # ---- PAYMENT RECORD ----
            payment = Payment()
            payment.order_id = order.id # type: ignore
            payment.provider = payment_provider # type: ignore
            payment.reference = payment_reference   # type: ignore
            payment.amount = total_amount   # type: ignore
            payment.status = "initiated"    # type: ignore
            session.add(payment)

            # ---- COMMIT (single atomic operation) ----
            session.commit()

            return order

        except (SQLAlchemyError, CheckoutError) as exc:
            # Rollback EVERYTHING (inventory, order, payment)
            session.rollback()
            raise CheckoutError(str(exc)) from exc
