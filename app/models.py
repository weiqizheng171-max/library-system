# app/models.py
from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    # ✅ 新增：存放加密后的密码
    hashed_password: Mapped[str] = mapped_column(String(200))

class BookInfo(Base):
    __tablename__ = "book_infos"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    author: Mapped[str] = mapped_column(String(50))
    publisher: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column(Float)
    intro: Mapped[Optional[str]] = mapped_column(String(500))
    items: Mapped[List["BookItem"]] = relationship(back_populates="info", lazy="selectin")

class BookItem(Base):
    __tablename__ = "book_items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    barcode: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    info_id: Mapped[int] = mapped_column(ForeignKey("book_infos.id"))
    status: Mapped[str] = mapped_column(String(20), default="available")
    info: Mapped["BookInfo"] = relationship(back_populates="items", lazy="selectin")