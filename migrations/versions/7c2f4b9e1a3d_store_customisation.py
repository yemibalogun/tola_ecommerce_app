"""Store customisation fields on tenant; category slug unique per tenant

Revision ID: 7c2f4b9e1a3d
Revises: 4dc2e3861df9
Create Date: 2026-09-19 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c2f4b9e1a3d'
down_revision = '4dc2e3861df9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tenant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tagline', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('about', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('logo', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('accent_color', sa.String(length=20), server_default='#6d5dfc', nullable=False))
        batch_op.add_column(sa.Column('currency_symbol', sa.String(length=8), server_default='₦', nullable=False))
        batch_op.add_column(sa.Column('hero_title', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('hero_subtitle', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('hero_image', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('contact_email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('contact_phone', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('instagram_url', sa.String(length=255), nullable=True))

    # Category slugs were globally unique, which stopped two stores from
    # using the same category name. Scope uniqueness to the tenant instead.
    # The old constraint came from db.create_all(), so drop it defensively.
    op.execute('ALTER TABLE category DROP CONSTRAINT IF EXISTS category_slug_key')
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_category_tenant_slug', ['tenant_id', 'slug'])


def downgrade():
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_constraint('uq_category_tenant_slug', type_='unique')
        batch_op.create_unique_constraint('category_slug_key', ['slug'])

    with op.batch_alter_table('tenant', schema=None) as batch_op:
        batch_op.drop_column('instagram_url')
        batch_op.drop_column('contact_phone')
        batch_op.drop_column('contact_email')
        batch_op.drop_column('hero_image')
        batch_op.drop_column('hero_subtitle')
        batch_op.drop_column('hero_title')
        batch_op.drop_column('currency_symbol')
        batch_op.drop_column('accent_color')
        batch_op.drop_column('logo')
        batch_op.drop_column('about')
        batch_op.drop_column('tagline')
