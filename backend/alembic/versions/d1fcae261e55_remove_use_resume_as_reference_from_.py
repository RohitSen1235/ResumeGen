"""Remove use_resume_as_reference from profiles

Revision ID: d1fcae261e55
Revises: 5446d2f51222
Create Date: 2025-08-22 11:32:21.026945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1fcae261e55'
down_revision: Union[str, None] = '5446d2f51222'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.drop_column('profiles', 'use_resume_as_reference')



def downgrade() -> None:

    op.add_column('profiles', sa.Column('use_resume_as_reference', sa.BOOLEAN(), autoincrement=False, nullable=False))


