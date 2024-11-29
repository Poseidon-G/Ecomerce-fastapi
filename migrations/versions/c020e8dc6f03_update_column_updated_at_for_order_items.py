"""update column updated_at for order_items

Revision ID: c020e8dc6f03
Revises: 425acfe94b26
Create Date: 2024-11-29 16:17:31.961519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c020e8dc6f03'
down_revision: Union[str, None] = '425acfe94b26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("order_items", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("order_items", sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("order_items", "updated_at")
    op.drop_column("order_items", "created_at")
