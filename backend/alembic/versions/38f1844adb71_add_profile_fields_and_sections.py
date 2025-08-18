"""add_profile_fields_and_sections

Revision ID: 38f1844adb71
Revises: 3dd41f694d38
Create Date: 2025-08-15 13:34:37.608274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '38f1844adb71'
down_revision: Union[str, None] = '3dd41f694d38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to profiles table (skip use_resume_as_reference as it already exists)
    op.add_column('profiles', sa.Column('portfolio_url', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('github_url', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('professional_title', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('profiles', sa.Column('use_resume_sections', sa.Boolean(), nullable=True, default=True))

    # Create work_experience table
    op.create_table('work_experience',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('current_job', sa.Boolean(), nullable=True, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('achievements', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('technologies', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_experience_user_id'), 'work_experience', ['user_id'], unique=False)

    # Create education table
    op.create_table('education',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution', sa.String(), nullable=False),
        sa.Column('degree', sa.String(), nullable=False),
        sa.Column('field_of_study', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('gpa', sa.Float(), nullable=True),
        sa.Column('achievements', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_education_user_id'), 'education', ['user_id'], unique=False)

    # Create skills table
    op.create_table('skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('proficiency', sa.Enum('Beginner', 'Intermediate', 'Advanced', 'Expert', name='proficiencylevel'), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skills_user_id'), 'skills', ['user_id'], unique=False)

    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('github_url', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('technologies', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('achievements', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_skills_user_id'), table_name='skills')
    op.drop_table('skills')
    op.drop_index(op.f('ix_education_user_id'), table_name='education')
    op.drop_table('education')
    op.drop_index(op.f('ix_work_experience_user_id'), table_name='work_experience')
    op.drop_table('work_experience')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS proficiencylevel')
    
    # Remove columns from profiles table (skip use_resume_as_reference as it existed before)
    op.drop_column('profiles', 'use_resume_sections')
    op.drop_column('profiles', 'summary')
    op.drop_column('profiles', 'professional_title')
    op.drop_column('profiles', 'github_url')
    op.drop_column('profiles', 'portfolio_url')
