from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 🌟 修复版引擎配置
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # ✅ 关键：每次操作前检查连接，防断连
    pool_recycle=3600,   # ✅ 关键：每小时自动回收连接
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
