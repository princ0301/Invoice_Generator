"""Authentication endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from supabase import Client
from app.database import get_supabase_client

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class AuthRequest(BaseModel):
    """Authentication request."""
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    """Authentication response with token."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: AuthRequest, supabase: Client = Depends(get_supabase_client)):
    """Register a new user."""
    response = supabase.auth.sign_up(credentials={"email": request.email, "password": request.password})
    if not response.user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed")
    if not response.session:
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Registration successful. Please check your email to confirm your account.")
    return AuthResponse(access_token=response.session.access_token, user_id=response.user.id, email=response.user.email)

@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest, supabase: Client = Depends(get_supabase_client)):
    """Login with email and password."""
    response = supabase.auth.sign_in_with_password(credentials={"email": request.email, "password": request.password})
    if not response.user or not response.session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return AuthResponse(access_token=response.session.access_token, user_id=response.user.id, email=response.user.email)
