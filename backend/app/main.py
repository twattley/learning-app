from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_pool
from app.routers import learn, math, questions


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(title="Recall", version="0.1.0", lifespan=lifespan)

# CORS — allow the React dev server and any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/api/v1")
app.include_router(learn.router, prefix="/api/v1")
app.include_router(math.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
