# app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- 用户与认证 ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str  # 注册时只要密码，不需要其他

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- 图书业务 (保持不变) ---
class BookInfoBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    price: float
    intro: Optional[str] = None

class BookInfoCreate(BookInfoBase):
    pass

class BookInfoResponse(BookInfoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookItemCreate(BaseModel):
    barcode: str
    info_id: int

class BookItemResponse(BaseModel):
    id: int
    barcode: str
    status: str
    info: BookInfoResponse 
    model_config = ConfigDict(from_attributes=True)

class BorrowReturnRequest(BaseModel):
    barcode: str