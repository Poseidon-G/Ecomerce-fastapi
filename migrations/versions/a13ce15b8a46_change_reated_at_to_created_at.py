"""change reated_at to created_at

Revision ID: a13ce15b8a46
Revises: 3480e048a345
Create Date: 2024-11-22 16:37:14.669294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a13ce15b8a46'
down_revision: Union[str, None] = '3480e048a345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename 'reated_at' to 'created_at' in 'users' table
    op.alter_column('users', 'reated_at', new_column_name='created_at')
    
    # Rename 'reated_at' to 'created_at' in 'orders' table
    # op.alter_column('orders', 'reated_at', new_column_name='created_at')
    
    # Add similar lines for other tables if needed
    op.alter_column('categories', 'reated_at', new_column_name='created_at')
    # op.alter_column('order_items', 'reated_at', new_column_name='created_at')

    op.alter_column('products', 'reated_at', new_column_name='created_at')
    # op.alter_column('reviews', 'reated_at', new_column_name='created_at')


def downgrade() -> None:
    op.alter_column('users', 'created_at', new_column_name='reated_at')

    # op.alter_column('orders', 'created_at', new_column_name='reated_at')

    op.alter_column('categories', 'created_at', new_column_name='reated_at')

    # op.alter_column('order_items', 'created_at', new_column_name='reated_at')

    op.alter_column('products', 'created_at', new_column_name='reated_at')

    # op.alter_column('reviews', 'created_at', new_column_name='reated_at')