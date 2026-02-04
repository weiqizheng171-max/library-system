# app/routers/books.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app import schemas, crud, auth, models

router = APIRouter()

# 1. 编目 (不需要登录可看，录入建议加锁，这里演示先不加)
@router.post("/catalog", response_model=schemas.BookInfoResponse, tags=["1. 图书编目"])
async def create_book_catalog(info: schemas.BookInfoCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_book_info(db, info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"录入失败: {str(e)}")

@router.get("/catalog", response_model=List[schemas.BookInfoResponse], tags=["1. 图书编目"])
async def get_book_catalog(db: AsyncSession = Depends(get_db)):
    return await crud.get_book_infos(db)

# 2. 馆藏
@router.post("/inventory", response_model=schemas.BookItemResponse, tags=["2. 馆藏管理"])
async def create_inventory_item(item: schemas.BookItemCreate, db: AsyncSession = Depends(get_db)):
    book_info = await crud.get_book_info_by_id(db, item.info_id)
    if not book_info:
        raise HTTPException(status_code=404, detail="找不到该书籍资料ID")
    try:
        return await crud.create_book_item(db, item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"入库失败: {str(e)}")

@router.get("/inventory", response_model=List[schemas.BookItemResponse], tags=["2. 馆藏管理"])
async def get_inventory_items(db: AsyncSession = Depends(get_db)):
    return await crud.get_book_items(db)

# 3. 流通 (🔒 加锁区域)
@router.post("/circulation/borrow", response_model=schemas.BookItemResponse, tags=["3. 借阅流通"])
async def borrow_book(
    request: schemas.BorrowReturnRequest, 
    db: AsyncSession = Depends(get_db),
    # 🔥🔥🔥 核心：必须带着 Token 才能调用这个函数
    current_user: models.User = Depends(auth.get_current_user)
):
    print(f"用户 {current_user.username} 正在借书...") # 可以在后台看到是谁借的
    db_item = await crud.get_book_item_by_barcode(db, request.barcode)
    if not db_item:
        raise HTTPException(status_code=404, detail="找不到该条码的书籍")
    if db_item.status != "available":
        raise HTTPException(status_code=400, detail="这本书已被借出")
    return await crud.update_book_status(db, db_item, "borrowed")

@router.post("/circulation/return", response_model=schemas.BookItemResponse, tags=["3. 借阅流通"])
async def return_book(
    request: schemas.BorrowReturnRequest, 
    db: AsyncSession = Depends(get_db),
    # 🔥🔥🔥 核心：必须带着 Token 才能调用这个函数
    current_user: models.User = Depends(auth.get_current_user)
):
    db_item = await crud.get_book_item_by_barcode(db, request.barcode)
    if not db_item:
        raise HTTPException(status_code=404, detail="找不到该条码的书籍")
    return await crud.update_book_status(db, db_item, "available")