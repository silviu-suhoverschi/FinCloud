"""
FinCloud Budget Service
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import accounts, transactions, budgets, categories
from app.api.v1.endpoints import auth, users, password_reset


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="FinCloud Budget Service",
    description="Budget and transaction management service",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "budget-service", "version": "0.1.0"}


# Include routers
# Authentication & Authorization
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(
    password_reset.router, prefix="/api/v1/password-reset", tags=["password-reset"]
)

# Business Logic
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(
    transactions.router, prefix="/api/v1/transactions", tags=["transactions"]
)
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "FinCloud Budget Service", "version": "0.1.0", "docs": "/docs"}
