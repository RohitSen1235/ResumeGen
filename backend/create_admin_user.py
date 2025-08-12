#!/usr/bin/env python3
"""
Script to create an admin user in the database.
This script can be used in production to create admin users.
"""

import sys
import argparse
import logging
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal, engine
from app.models import User, Profile
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def create_admin_user(email: str, password: str, name: str = None):
    """Create an admin user in the database"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            if existing_user.is_admin:
                logger.info(f"Admin user with email {email} already exists")
                return True
            else:
                # Update existing user to admin
                existing_user.is_admin = True
                if password:
                    existing_user.hashed_password = hash_password(password)
                db.commit()
                logger.info(f"Updated existing user {email} to admin")
                return True
        
        # Create new admin user
        hashed_password = hash_password(password)
        admin_user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password,
            is_admin=True,
            user_type="other"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create profile for admin user if name is provided
        if name:
            profile = Profile(
                id=uuid.uuid4(),
                user_id=admin_user.id,
                name=name,
                professional_info={
                    "id": str(uuid.uuid4()),
                    "first_name": name.split()[0] if name else "Admin",
                    "last_name": name.split()[-1] if name and len(name.split()) > 1 else "User",
                    "summary": "System Administrator"
                }
            )
            db.add(profile)
            db.commit()
            logger.info(f"Created profile for admin user: {name}")
        
        logger.info(f"Successfully created admin user: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_admin_users():
    """List all admin users in the database"""
    db = SessionLocal()
    try:
        admin_users = db.query(User).filter(User.is_admin == True).all()
        if not admin_users:
            logger.info("No admin users found")
            return
        
        logger.info("Admin users:")
        for user in admin_users:
            profile_name = ""
            if user.profile and user.profile.name:
                profile_name = f" ({user.profile.name})"
            logger.info(f"- {user.email}{profile_name} (ID: {user.id})")
            
    except Exception as e:
        logger.error(f"Error listing admin users: {e}")
    finally:
        db.close()

def make_user_admin(email: str):
    """Make an existing user an admin"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.error(f"User with email {email} not found")
            return False
        
        if user.is_admin:
            logger.info(f"User {email} is already an admin")
            return True
        
        user.is_admin = True
        db.commit()
        logger.info(f"Successfully made user {email} an admin")
        return True
        
    except Exception as e:
        logger.error(f"Error making user admin: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def remove_admin_privileges(email: str):
    """Remove admin privileges from a user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.error(f"User with email {email} not found")
            return False
        
        if not user.is_admin:
            logger.info(f"User {email} is not an admin")
            return True
        
        user.is_admin = False
        db.commit()
        logger.info(f"Successfully removed admin privileges from user {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing admin privileges: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Admin user management')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create admin command
    create_parser = subparsers.add_parser('create', help='Create a new admin user')
    create_parser.add_argument('email', help='Admin user email')
    create_parser.add_argument('password', help='Admin user password')
    create_parser.add_argument('--name', help='Admin user name (optional)')
    
    # List admins command
    subparsers.add_parser('list', help='List all admin users')
    
    # Make admin command
    make_admin_parser = subparsers.add_parser('make-admin', help='Make an existing user an admin')
    make_admin_parser.add_argument('email', help='User email to make admin')
    
    # Remove admin command
    remove_admin_parser = subparsers.add_parser('remove-admin', help='Remove admin privileges from a user')
    remove_admin_parser.add_argument('email', help='Admin user email to remove privileges from')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = False
    
    if args.command == 'create':
        success = create_admin_user(args.email, args.password, args.name)
    elif args.command == 'list':
        list_admin_users()
        success = True
    elif args.command == 'make-admin':
        success = make_user_admin(args.email)
    elif args.command == 'remove-admin':
        success = remove_admin_privileges(args.email)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
