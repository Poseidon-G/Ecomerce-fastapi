"""update column updated_at for order

Revision ID: 425acfe94b26
Revises: a13ce15b8a46
Create Date: 2024-11-29 16:14:36.986473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '425acfe94b26'
down_revision: Union[str, None] = 'a13ce15b8a46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # alter add column updated_at
    op.add_column("orders", sa.Column("updated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    # alter drop column updated_at
    op.drop_column("orders", "updated_at")
