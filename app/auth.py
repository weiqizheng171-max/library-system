# app/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import schemas, database, models, crud
from sqlalchemy.ext.asyncio import AsyncSession

# 1. 配置参数 (真实开发中这些要放在 .env 里)
SECRET_KEY = "your-very-secret-key-change-me"  # 密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 2. 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. 定义 Token 获取方式 (告诉 Swagger UI 哪里输入 token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- 工具函数 ---

def verify_password(plain_password, hashed_password):
    """核对密码是否正确"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """把明文密码加密成乱码"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """生成 JWT Token (发门票)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 依赖注入：获取当前登录用户 ---
# 这是一个拦截器，所有需要登录的接口都要用它
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_Unauthorized,
        detail="登录已过期或无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # 查数据库确认用户存在
    user = await crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user