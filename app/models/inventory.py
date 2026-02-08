from app.extensions.db import db


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenant.id"),
        nullable=False,
        index=True
    )

    variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variant.id"),
        nullable=False,
        unique=True
    )

    quantity_available = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
