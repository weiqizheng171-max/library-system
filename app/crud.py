# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
# 注意：这里需要从 auth 导入哈希函数，但为了避免循环导入，我们在 create_user 里处理
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 用户相关 ---
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # 1. 密码加密
    hashed_pwd = pwd_context.hash(user.password)
    # 2. 创建对象
    db_user = models.User(username=user.username, hashed_password=hashed_pwd)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- 图书相关 (保持不变) ---
async def create_book_info(db: AsyncSession, info: schemas.BookInfoCreate):
    db_info = models.BookInfo(**info.model_dump())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info

async def get_book_infos(db: AsyncSession):
    result = await db.execute(select(models.BookInfo))
    return result.scalars().all()

async def create_book_item(db: AsyncSession, item: schemas.BookItemCreate):
    db_item = models.BookItem(barcode=item.barcode, info_id=item.info_id, status="available")
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_book_items(db: AsyncSession):
    result = await db.execute(select(models.BookItem))
    return result.scalars().all()

async def get_book_info_by_id(db: AsyncSession, info_id: int):
    return await db.get(models.BookInfo, info_id)

async def get_book_item_by_barcode(db: AsyncSession, barcode: str):
    query = select(models.BookItem).where(models.BookItem.barcode == barcode)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_book_status(db: AsyncSession, db_item: models.BookItem, new_status: str):
    db_item.status = new_status
    await db.commit()
    await db.refresh(db_item)
    return db_item