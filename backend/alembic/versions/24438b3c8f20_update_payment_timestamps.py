"""update_payment_timestamps

Revision ID: 24438b3c8f20
Revises: 91756eb83cc2
Create Date: 2024-12-30 14:34:47.123849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '24438b3c8f20'
down_revision: Union[str, None] = '91756eb83cc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make created_at non-nullable and ensure it has server_default
    op.alter_column('payments', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text('now()')
    )
    
    # Update updated_at to have both server_default and onupdate
    op.alter_column('payments', 'updated_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=sa.text('now()'),
        server_onupdate=sa.text('now()')
    )


def downgrade() -> None:
    # Revert created_at changes
    op.alter_column('payments', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=None
    )
    
    # Revert updated_at changes
    op.alter_column('payments', 'updated_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=None,
        server_onupdate=None
    )
