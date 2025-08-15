"""fix_profile_sections_schema

Revision ID: fix_profile_sections_schema
Revises: 38f1844adb71
Create Date: 2025-08-15 19:19:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '38f1844adb71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing tables with wrong schema
    op.drop_table('projects')
    op.drop_table('skills')
    op.drop_table('education')
    op.drop_table('work_experience')
    
    # Drop the enum type if it exists
    op.execute('DROP TYPE IF EXISTS proficiencylevel')
    
    # Create work_experiences table (note the plural name)
    op.create_table('work_experiences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('current_job', sa.Boolean(), nullable=False, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('technologies', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_experiences_id'), 'work_experiences', ['id'], unique=False)
    op.create_index(op.f('ix_work_experiences_profile_id'), 'work_experiences', ['profile_id'], unique=False)

    # Create educations table (note the plural name)
    op.create_table('educations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution', sa.String(), nullable=False),
        sa.Column('degree', sa.String(), nullable=False),
        sa.Column('field_of_study', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('gpa', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_educations_id'), 'educations', ['id'], unique=False)
    op.create_index(op.f('ix_educations_profile_id'), 'educations', ['profile_id'], unique=False)

    # Create skills table
    op.create_table('skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('proficiency', sa.String(), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skills_id'), 'skills', ['id'], unique=False)
    op.create_index(op.f('ix_skills_profile_id'), 'skills', ['profile_id'], unique=False)

    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('github_url', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('technologies', sa.JSON(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_profile_id'), 'projects', ['profile_id'], unique=False)

    # Create publications table
    op.create_table('publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('publisher', sa.String(), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('authors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_publications_id'), 'publications', ['id'], unique=False)
    op.create_index(op.f('ix_publications_profile_id'), 'publications', ['profile_id'], unique=False)

    # Create volunteer_works table
    op.create_table('volunteer_works',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('cause', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('current_role', sa.Boolean(), nullable=False, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_volunteer_works_id'), 'volunteer_works', ['id'], unique=False)
    op.create_index(op.f('ix_volunteer_works_profile_id'), 'volunteer_works', ['profile_id'], unique=False)


def downgrade() -> None:
    # Drop new tables
    op.drop_index(op.f('ix_volunteer_works_profile_id'), table_name='volunteer_works')
    op.drop_index(op.f('ix_volunteer_works_id'), table_name='volunteer_works')
    op.drop_table('volunteer_works')
    
    op.drop_index(op.f('ix_publications_profile_id'), table_name='publications')
    op.drop_index(op.f('ix_publications_id'), table_name='publications')
    op.drop_table('publications')
    
    op.drop_index(op.f('ix_projects_profile_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    op.drop_index(op.f('ix_skills_profile_id'), table_name='skills')
    op.drop_index(op.f('ix_skills_id'), table_name='skills')
    op.drop_table('skills')
    
    op.drop_index(op.f('ix_educations_profile_id'), table_name='educations')
    op.drop_index(op.f('ix_educations_id'), table_name='educations')
    op.drop_table('educations')
    
    op.drop_index(op.f('ix_work_experiences_profile_id'), table_name='work_experiences')
    op.drop_index(op.f('ix_work_experiences_id'), table_name='work_experiences')
    op.drop_table('work_experiences')
