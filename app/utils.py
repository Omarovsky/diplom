from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app import schemas

SECRET_KEY = "7377f8cbcf4c4f0440a5eb9ace263a2e9b7225f501055a32d1e1eac222a367fd6fcb80224536458e10349428d190cec92cf50103f3973c9b61586f5123fdbe4bccc833d07f56c8d4227e4a8a4e9890bc2b5ea72ecba14fbb70b018f798c6bbe9c0d30e8283b5ec1910faad8dad9f83cd4e954653ed2807ed7b548bd13889cd69401db03e058649fa8e41a04506b13638e0c05c66096b2ad911816cda2b2cfc957cebf3f0813bd3e067dc6ec4bf1b8208eb763c2676be5a2a47defec16583e6234f5befcc3451c4e56669c0d607c6e5a0bfd9416b64eeda2556739e3f83f5ee4577de8e14e77e3b86880901404477bdab734029f622542d059e72465fe57f3996"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])