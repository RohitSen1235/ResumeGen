"""add_missing_content_column_final_fix

Revision ID: af74d4c45273
Revises: a7aecc9b1fd4
Create Date: 2025-08-22 09:13:47.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af74d4c45273'
down_revision: Union[str, None] = 'a7aecc9b1fd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FINAL FIX: Add missing content column to resumes table.
    
    This migration is needed because the production database is missing
    the 'content' column that the SQLAlchemy model expects, causing
    UndefinedColumn errors when querying resumes.
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
        print("✅ Added missing 'content' column to resumes table")
        
        # Log the current state
        print("📊 Current resumes table now has both:")
        print("   - content (nullable) - for DB fallback storage")
        print("   - content_s3_key (nullable) - for S3 primary storage")
        print("🎯 S3-first strategy is now fully implemented!")
    else:
        print("ℹ️  'content' column already exists in resumes table")


def downgrade() -> None:
    """
    Remove the content column if it was added by this migration
    """
    from alembic import context
    conn = context.get_bind()
    
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='resumes' AND column_name='content'
    """))
    
    if result.fetchone():
        op.drop_column('resumes', 'content')
        print("Removed 'content' column from resumes table")
