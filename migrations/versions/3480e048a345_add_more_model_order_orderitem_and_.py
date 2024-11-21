"""Add more model order, orderitem and review

Revision ID: 3480e048a345
Revises: 9904e0e3384a
Create Date: 2024-11-21 23:55:54.607191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.utils.text import slugify
# revision identifiers, used by Alembic.
revision: str = '3480e048a345'
down_revision: Union[str, None] = '9904e0e3384a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'phone' column to 'users' table
    op.alter_column('users', 'phone', existing_type=sa.String(length=20), nullable=True)

    # Add 'slug' column to 'categories' table
    op.add_column('categories', sa.Column('slug', sa.String(length=100), nullable=True, unique=True))

    # Update existing 'categories' records to set the 'slug' field
    # This requires generating slugs from existing names
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT id, name FROM categories"))
    for row in result:
        new_slug = slugify(row[1])  # Access name by index 1
        connection.execute(
            sa.text("UPDATE categories SET slug = :slug WHERE id = :id"),
            {"slug": new_slug, "id": row[0]}  # Access id by index 0
        )

    # Alter 'slug' column to be non-nullable and unique
    op.alter_column('categories', 'slug',
                    existing_type=sa.String(length=100),
                    nullable=False)
    op.create_unique_constraint('uq_categories_slug', 'categories', ['slug'])

    # Create 'orders' table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total', sa.Float(), nullable=False),
        sa.Column('is_paid', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_shipped', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)

    # Create 'order_items' table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)

    # Create 'reviews' table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)


def downgrade() -> None:
   # Drop 'reviews' table and its index
    op.drop_index('ix_reviews_id', table_name='reviews')
    op.drop_table('reviews')

    # Drop 'order_items' table and its index
    op.drop_index('ix_order_items_id', table_name='order_items')
    op.drop_table('order_items')

    # Drop 'orders' table and its index
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_table('orders')

    # Drop slug unique constraint and column from 'categories' table
    op.drop_constraint('uq_categories_slug', 'categories', type_='unique')
    op.drop_column('categories', 'slug')

    # Revert 'phone' column in 'users' table to non-nullable
    op.alter_column('users', 'phone',
                    existing_type=sa.String(length=20),
                    nullable=False)