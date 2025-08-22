"""fix_s3_integration_make_content_and_s3_key_nullable

Revision ID: a7aecc9b1fd4
Revises: 1dad7cc349e9
Create Date: 2025-08-22 07:34:18.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7aecc9b1fd4'
down_revision: Union[str, None] = '1dad7cc349e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fix S3 integration by making both content and content_s3_key nullable.
    This aligns with the S3-first storage strategy where:
    - content_s3_key is NULL when S3 upload fails (fallback to DB content)
    - content is NULL when S3 upload succeeds (S3 is primary storage)
    """
    from alembic import context
    conn = context.get_bind()
    
    # Check if content_s3_key column exists and make it nullable if it exists
    result = conn.execute(sa.text("""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name='resumes' AND column_name='content_s3_key'
    """))
    content_s3_key_info = result.fetchone()
    
    if content_s3_key_info:
        # Column exists, make it nullable if it's not already
        if content_s3_key_info[1] == 'NO':  # is_nullable = 'NO'
            op.alter_column('resumes', 'content_s3_key',
                            existing_type=sa.String(),
                            nullable=True)
        
        # Clear empty string values that were set in previous migration
        op.execute("UPDATE resumes SET content_s3_key = NULL WHERE content_s3_key = ''")
    
    # Check if content column exists and make it nullable if it exists
    result = conn.execute(sa.text("""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name='resumes' AND column_name='content'
    """))
    content_info = result.fetchone()
    
    if content_info:
        # Column exists, make it nullable if it's not already
        if content_info[1] == 'NO':  # is_nullable = 'NO'
            op.alter_column('resumes', 'content',
                            existing_type=sa.String(),
                            nullable=True)


def downgrade() -> None:
    """
    Revert changes - make both fields NOT NULL again
    """
    # Fill NULL values before making NOT NULL
    op.execute("UPDATE resumes SET content_s3_key = '' WHERE content_s3_key IS NULL")
    op.execute("UPDATE resumes SET content = '' WHERE content IS NULL")
    
    # Make fields NOT NULL again
    op.alter_column('resumes', 'content',
                    existing_type=sa.String(),
                    nullable=False)
    
    op.alter_column('resumes', 'content_s3_key',
                    existing_type=sa.String(),
                    nullable=False)
