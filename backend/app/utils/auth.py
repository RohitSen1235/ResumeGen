from datetime import datetime, timedelta
from typing import Optional
import redis
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
import os

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=True
)

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-keep-it-secret')  # In production, set SECRET_KEY in .env
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme with correct token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token and store in Redis."""
    to_encode = data.copy()
    expire_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expire_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store token in Redis with expiration
    print(f"Storing token in Redis for user: {data.get('sub')}")
    redis_client.setex(
        f"token:{encoded_jwt}",
        time=expire_delta,
        value=data.get("sub")
    )
    return encoded_jwt

def refresh_access_token(token: str) -> str:
    """Refresh an access token that is near expiration."""
    try:
        # Verify token is still valid but near expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError("Invalid token payload")
            
        # Check if token is within last 5 minutes of expiration
        expiration = datetime.utcfromtimestamp(payload["exp"])
        if (expiration - datetime.utcnow()) > timedelta(minutes=5):
            raise JWTError("Token not eligible for refresh")
            
        # Create new token with fresh expiration
        new_token = create_access_token({"sub": email})
        
        # Delete old token from Redis
        redis_client.delete(f"token:{token}")
        
        return new_token
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token with Redis cache."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Always validate JWT first
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Check Redis cache
        cached_email = redis_client.get(f"token:{token}")
        if cached_email and cached_email == email:
            print(f"Cache hit for user: {email}")
            user = db.query(User).filter(User.email == email).first()
            if user:
                # Refresh Redis expiration
                redis_client.expire(f"token:{token}", time=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
                return user
        
        print("Cache miss - falling back to database lookup")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
            
        # Store validated token in Redis
        redis_client.setex(
            f"token:{token}",
            time=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            value=email
        )
        
        return user
        
    except JWTError:
        raise credentials_exception

def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the email if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

    print("Cache miss - falling back to database lookup")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    # Store validated token in Redis
    redis_client.setex(
        f"token:{token}",
        time=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        value=email
    )
    
    return user
