# main.py
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import books, auth  # ✅ 导入 auth
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> 正在初始化数据库...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(">>> ✅ 系统启动成功！")
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan, title="图书管理系统 (安全版)")

app.include_router(books.router)
app.include_router(auth.router) # ✅ 注册 auth 路由

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)