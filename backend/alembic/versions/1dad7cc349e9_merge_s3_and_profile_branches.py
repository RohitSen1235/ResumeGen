"""merge s3 and profile branches

Revision ID: 1dad7cc349e9
Revises: 9a40101fbfdc, fbcbd601f235
Create Date: 2025-08-21 17:10:20.858305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dad7cc349e9'
down_revision: Union[str, None] = ('9a40101fbfdc', 'fbcbd601f235')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
