from fastapi import FastAPI
import uvicorn

from db.db import create_tables
from routers.files import router as file_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("Tables created")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router=file_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

