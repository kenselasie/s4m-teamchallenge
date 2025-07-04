from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import create_tables, seed_demo_user
from app.routers.pdf_router import router as pdf_router
from app.routers.user_router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    seed_demo_user()
    yield

app = FastAPI(
    title="Code Challenge API",
    description="API for uploading, parsing, and searching PDF documents",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "PDF Parser API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"} 