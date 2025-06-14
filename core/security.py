from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from infrastructure.database.models import UserModel
from infrastructure.database.session import get_db
from core.config import settings
from itsdangerous import URLSafeTimedSerializer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, UnknownHashError):
        return False


def hash_password(pwd):
    return pwd_context.hash(pwd)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[UserModel]:
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None

    try:
        token = token.split(" ")[1]
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            return None

        return db.query(UserModel).filter(UserModel.username == username).first()
    except JWTError:
        return None


async def get_current_user_optional(
        request: Request,
        db: Session = Depends(get_db)
) -> Optional[UserModel]:
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(
            token.split()[1],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    return db.query(UserModel).filter(UserModel.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None

    print(f"Checking password for user: {username}")
    print(f"Stored hash: {user.password_hash}")

    try:
        if not verify_password(password, user.password_hash):
            return None
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return None

    if not user.is_active:
        return None

    return user

def generate_csrf_token() -> str:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt='csrf')
    return serializer.dumps('csrf_token')

def validate_csrf_token(token: str) -> bool:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt='csrf')
    try:
        serializer.loads(token, max_age=3600)
        return True
    except:
        return False