"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, clients, invoices
from app.database import get_supabase_client

app = FastAPI(
    title="Invoice Generator API",
    description="API for managing invoices and clients",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(invoices.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Invoice Generator API", "version": "0.1.0"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "api": "operational",
        "supabase": "unknown"
    }

    try:
        supabase = get_supabase_client()

        supabase.table("clients").select("id").limit(1).execute()
        health_status["supabase"] = "connected"
    except Exception as e:
        health_status["supabase"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        health_status["message"] = "Supabase connection failed. Check backend/SETUP_REQUIRED.md"
    
    return health_status
