"""Client management endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from supabase import Client
from app.api.dependencies import get_current_user, get_authenticated_supabase

router = APIRouter(prefix="/api/clients", tags=["clients"])

class ClientCreateRequest(BaseModel):
    """Request model for creating a client."""
    name: str = Field(..., min_length=1)
    email: EmailStr
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    zip_code: str = Field(..., min_length=1, alias="zipCode")
    country: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)

class ClientUpdateRequest(BaseModel):
    """Request model for updating a client."""
    name: str | None = Field(None, min_length=1)
    email: EmailStr | None = None
    street: str | None = Field(None, min_length=1)
    city: str | None = Field(None, min_length=1)
    state: str | None = Field(None, min_length=1)
    zip_code: str | None = Field(None, min_length=1, alias="zipCode")
    country: str | None = Field(None, min_length=1)
    phone: str | None = Field(None, min_length=1)

class ClientResponse(BaseModel):
    """Response model for client data."""
    model_config = {"populate_by_name": True}
    id: str
    user_id: str = Field(alias="userId")
    name: str
    email: str
    street: str
    city: str
    state: str
    zip_code: str = Field(alias="zipCode")
    country: str
    phone: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    request: ClientCreateRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Create a new client."""
    client_data = {
        "user_id": current_user["id"],
        "name": request.name,
        "email": request.email,
        "street": request.street,
        "city": request.city,
        "state": request.state,
        "zip_code": request.zip_code,
        "country": request.country,
        "phone": request.phone
    }
    response = supabase.table("clients").insert(client_data).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create client")
    return response.data[0]

@router.get("", response_model=List[ClientResponse])
async def list_clients(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """List all clients for the authenticated user."""
    response = supabase.table("clients").select("*").eq("user_id", current_user["id"]).execute()
    return response.data

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Get a specific client by ID."""
    response = supabase.table("clients").select("*").eq("id", str(client_id)).eq("user_id", current_user["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return response.data[0]

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    request: ClientUpdateRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Update a client."""
    update_data = {k: v for k, v in request.model_dump(by_alias=False, exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    response = supabase.table("clients").update(update_data).eq("id", str(client_id)).eq("user_id", current_user["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return response.data[0]

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Delete a client."""
    invoice_check = supabase.table("invoices").select("id").eq("client_id", str(client_id)).eq("user_id", current_user["id"]).execute()
    if invoice_check.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete client with associated invoices")
    response = supabase.table("clients").delete().eq("id", str(client_id)).eq("user_id", current_user["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return None
