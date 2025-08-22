"""add_cascade_delete_constraints_for_user_cleanup

Revision ID: cascade_delete_user_cleanup
Revises: af74d4c45273
Create Date: 2025-01-22 15:09:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cascade_delete_user_cleanup'
down_revision = 'af74d4c45273'
branch_labels = None
depends_on = None


def upgrade():
    """Add CASCADE delete constraints for complete user data cleanup"""
    
    # Drop existing foreign key constraints and recreate with CASCADE
    
    # 1. Update profiles.user_id foreign key to CASCADE
    op.drop_constraint('profiles_user_id_fkey', 'profiles', type_='foreignkey')
    op.create_foreign_key(
        'profiles_user_id_fkey', 
        'profiles', 
        'users', 
        ['user_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 2. Update resumes.profile_id foreign key to CASCADE
    op.drop_constraint('resumes_profile_id_fkey', 'resumes', type_='foreignkey')
    op.create_foreign_key(
        'resumes_profile_id_fkey', 
        'resumes', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 3. Update work_experiences.profile_id foreign key to CASCADE
    op.drop_constraint('work_experiences_profile_id_fkey', 'work_experiences', type_='foreignkey')
    op.create_foreign_key(
        'work_experiences_profile_id_fkey', 
        'work_experiences', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 4. Update educations.profile_id foreign key to CASCADE
    op.drop_constraint('educations_profile_id_fkey', 'educations', type_='foreignkey')
    op.create_foreign_key(
        'educations_profile_id_fkey', 
        'educations', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 5. Update skills.profile_id foreign key to CASCADE
    op.drop_constraint('skills_profile_id_fkey', 'skills', type_='foreignkey')
    op.create_foreign_key(
        'skills_profile_id_fkey', 
        'skills', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 6. Update projects.profile_id foreign key to CASCADE
    op.drop_constraint('projects_profile_id_fkey', 'projects', type_='foreignkey')
    op.create_foreign_key(
        'projects_profile_id_fkey', 
        'projects', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 7. Update publications.profile_id foreign key to CASCADE
    op.drop_constraint('publications_profile_id_fkey', 'publications', type_='foreignkey')
    op.create_foreign_key(
        'publications_profile_id_fkey', 
        'publications', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 8. Update volunteer_works.profile_id foreign key to CASCADE
    op.drop_constraint('volunteer_works_profile_id_fkey', 'volunteer_works', type_='foreignkey')
    op.create_foreign_key(
        'volunteer_works_profile_id_fkey', 
        'volunteer_works', 
        'profiles', 
        ['profile_id'], 
        ['id'], 
        ondelete='CASCADE'
    )


def downgrade():
    """Remove CASCADE delete constraints and restore original foreign keys"""
    
    # Restore original foreign key constraints without CASCADE
    
    # 1. Restore profiles.user_id foreign key without CASCADE
    op.drop_constraint('profiles_user_id_fkey', 'profiles', type_='foreignkey')
    op.create_foreign_key(
        'profiles_user_id_fkey', 
        'profiles', 
        'users', 
        ['user_id'], 
        ['id']
    )
    
    # 2. Restore resumes.profile_id foreign key without CASCADE
    op.drop_constraint('resumes_profile_id_fkey', 'resumes', type_='foreignkey')
    op.create_foreign_key(
        'resumes_profile_id_fkey', 
        'resumes', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
    
    # 3. Restore work_experiences.profile_id foreign key without CASCADE
    op.drop_constraint('work_experiences_profile_id_fkey', 'work_experiences', type_='foreignkey')
    op.create_foreign_key(
        'work_experiences_profile_id_fkey', 
        'work_experiences', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
    
    # 4. Restore educations.profile_id foreign key without CASCADE
    op.drop_constraint('educations_profile_id_fkey', 'educations', type_='foreignkey')
    op.create_foreign_key(
        'educations_profile_id_fkey', 
        'educations', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
    
    # 5. Restore skills.profile_id foreign key without CASCADE
    op.drop_constraint('skills_profile_id_fkey', 'skills', type_='foreignkey')
    op.create_foreign_key(
        'skills_profile_id_fkey', 
        'skills', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
    
    # 6. Restore projects.profile_id foreign key without CASCADE
    op.drop_constraint('projects_profile_id_fkey', 'projects', type_='foreignkey')
    op.create_foreign_key(
        'projects_profile_id_fkey', 
        'projects', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
    
    # 7. Restore publications.profile_id foreign key without CASCADE
    op.drop_constraint('publications_profile_id_fkey', 'publications', type_='foreignkey')
    op.create_foreign_key(
        'publications_profile_id_fkey', 
        'publications', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
    
    # 8. Restore volunteer_works.profile_id foreign key without CASCADE
    op.drop_constraint('volunteer_works_profile_id_fkey', 'volunteer_works', type_='foreignkey')
    op.create_foreign_key(
        'volunteer_works_profile_id_fkey', 
        'volunteer_works', 
        'profiles', 
        ['profile_id'], 
        ['id']
    )
