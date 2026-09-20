"""Support guest orders: optional user, inline customer details, optional variant

Revision ID: 9f41c7b2de08
Revises: 7c2f4b9e1a3d
Create Date: 2026-09-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f41c7b2de08'
down_revision = '7c2f4b9e1a3d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        # Shoppers check out without an account
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=True)
        batch_op.add_column(sa.Column('customer_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('customer_email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('customer_phone', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('shipping_address', sa.Text(), nullable=True))

    with op.batch_alter_table('order_item', schema=None) as batch_op:
        # Products can be sold without variants
        batch_op.alter_column('variant_id', existing_type=sa.Integer(), nullable=True)


def downgrade():
    # Rows added since the upgrade may not satisfy the old NOT NULL constraints,
    # so clear out anything that would block the rollback.
    op.execute('DELETE FROM order_item WHERE variant_id IS NULL')
    op.execute('DELETE FROM order_item WHERE order_id IN (SELECT id FROM "order" WHERE user_id IS NULL)')
    op.execute('DELETE FROM "order" WHERE user_id IS NULL')

    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.alter_column('variant_id', existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('shipping_address')
        batch_op.drop_column('customer_phone')
        batch_op.drop_column('customer_email')
        batch_op.drop_column('customer_name')
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
