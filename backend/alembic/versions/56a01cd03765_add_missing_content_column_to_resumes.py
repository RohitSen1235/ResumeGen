"""add_missing_content_column_to_resumes

Revision ID: 56a01cd03765
Revises: bbca5f148aae
Create Date: 2025-08-22 08:58:59.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56a01cd03765'
down_revision: Union[str, None] = 'bbca5f148aae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add missing content column to resumes table if it doesn't exist.
    This fixes the production issue where the model expects a content column
    but it doesn't exist in the database.
    """
    from alembic import context
    conn = context.get_bind()
    
    # Check if content column exists in resumes table
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='resumes' AND column_name='content'
    """))
    
    if not result.fetchone():
        # Column doesn't exist, add it as nullable (S3-first strategy)
        op.add_column('resumes', sa.Column('content', sa.String(), nullable=True))
        print("Added missing 'content' column to resumes table")
    else:
        print("'content' column already exists in resumes table")


def downgrade() -> None:
    """
    Remove the content column if it was added by this migration
    """
    # Only drop if it exists
    from alembic import context
    conn = context.get_bind()
    
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='resumes' AND column_name='content'
    """))
    
    if result.fetchone():
        op.drop_column('resumes', 'content')
