"""Invoice management endpoints."""
from typing import List
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from supabase import Client
from app.api.dependencies import get_current_user, get_authenticated_supabase
from app.models import InvoiceStatus, Invoice, LineItem, Client as ClientModel
from app.services import PDFExportService

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

class LineItemRequest(BaseModel):
    """Request model for line items."""
    description: str = Field(..., min_length=1)
    quantity: Decimal = Field(..., gt=0)
    unit_rate: Decimal = Field(..., gt=0, alias="unitRate")

class InvoiceCreateRequest(BaseModel):
    """Request model for creating an invoice."""
    client_id: str = Field(..., alias="clientId")
    invoice_number: str = Field(..., min_length=1, alias="invoiceNumber")
    invoice_date: date = Field(..., alias="invoiceDate")
    due_date: date = Field(..., alias="dueDate")
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, alias="taxRate")
    line_items: List[LineItemRequest] = Field(..., min_length=1, alias="lineItems")

class InvoiceUpdateRequest(BaseModel):
    """Request model for updating an invoice."""
    model_config = {
        "json_schema_extra": {
            "example": {
                "clientId": "123e4567-e89b-12d3-a456-426614174000",
                "invoiceNumber": "INV-2024-002",
                "invoiceDate": "2024-01-20",
                "dueDate": "2024-02-20",
                "taxRate": "10",
                "status": "draft",
                "lineItems": [
                    {
                        "description": "Updated Service",
                        "quantity": "5",
                        "unitRate": "200"
                    }
                ]
            }
        }
    }
    
    client_id: str | None = Field(None, alias="clientId")
    invoice_number: str | None = Field(None, min_length=1, alias="invoiceNumber")
    invoice_date: date | None = Field(None, alias="invoiceDate")
    due_date: date | None = Field(None, alias="dueDate")
    tax_rate: Decimal | None = Field(None, ge=0, le=100, alias="taxRate")
    status: InvoiceStatus | None = None
    line_items: List[LineItemRequest] | None = Field(None, alias="lineItems")

class LineItemResponse(BaseModel):
    """Response model for line items."""
    model_config = {"populate_by_name": True}
    
    id: str
    invoice_id: str = Field(alias="invoiceId")
    description: str
    quantity: str
    unit_rate: str = Field(alias="unitRate")

class ClientSummary(BaseModel):
    """Summary of client information for invoice response."""
    model_config = {"populate_by_name": True}
    
    id: str
    name: str
    email: str
    street: str
    city: str
    state: str
    zip_code: str = Field(alias="zipCode")
    country: str
    phone: str

class InvoiceResponse(BaseModel):
    """Response model for invoice data."""
    model_config = {"populate_by_name": True}
    
    id: str
    user_id: str = Field(alias="userId")
    client_id: str = Field(alias="clientId")
    invoice_number: str = Field(alias="invoiceNumber")
    invoice_date: str = Field(alias="invoiceDate")
    due_date: str = Field(alias="dueDate")
    tax_rate: str = Field(alias="taxRate")
    status: str
    sent_date: str | None = Field(alias="sentDate")
    paid_date: str | None = Field(alias="paidDate")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    line_items: List[LineItemResponse] = Field(default_factory=list, alias="lineItems")
    client: ClientSummary | None = None
    subtotal: str | None = None
    tax: str | None = None
    total: str | None = None

@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: InvoiceCreateRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Create a new invoice with line items."""
    try:

        if request.due_date < request.invoice_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be before invoice date"
            )

        if not request.line_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one line item is required"
            )

        invoice_data = {
            "user_id": current_user["id"],
            "client_id": request.client_id,
            "invoice_number": request.invoice_number,
            "invoice_date": request.invoice_date.isoformat(),
            "due_date": request.due_date.isoformat(),
            "tax_rate": str(request.tax_rate),
            "status": InvoiceStatus.DRAFT.value
        }
        
        invoice_response = supabase.table("invoices").insert(invoice_data).execute()
        
        if not invoice_response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create invoice"
            )
        
        invoice = invoice_response.data[0]
        invoice_id = invoice["id"]

        line_items_data = [
            {
                "invoice_id": invoice_id,
                "description": item.description,
                "quantity": str(item.quantity),
                "unit_rate": str(item.unit_rate)
            }
            for item in request.line_items
        ]
        
        line_items_response = supabase.table("line_items").insert(line_items_data).execute()

        return await get_invoice(UUID(invoice_id), current_user, supabase)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[InvoiceResponse])
async def list_invoices(
    status_filter: str | None = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """List all invoices for the authenticated user."""
    try:
        query = supabase.table("invoices")\
            .select("*, line_items(*), clients(*)")\
            .eq("user_id", current_user["id"])
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.execute()

        invoices = []
        for invoice_data in response.data:
            invoice = _transform_invoice_response(invoice_data)
            invoices.append(invoice)
        
        return invoices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Get a specific invoice by ID."""
    try:
        response = supabase.table("invoices")\
            .select("*, line_items(*), clients(*)")\
            .eq("id", str(invoice_id))\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return _transform_invoice_response(response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    request: InvoiceUpdateRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Update an invoice."""
    try:

        existing_response = supabase.table("invoices")\
            .select("invoice_date, due_date")\
            .eq("id", str(invoice_id))\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        existing_invoice = existing_response.data[0]

        update_data = {}
        if request.client_id is not None:
            update_data["client_id"] = request.client_id
        if request.invoice_number is not None:
            update_data["invoice_number"] = request.invoice_number
        if request.invoice_date is not None:
            update_data["invoice_date"] = request.invoice_date.isoformat()
        if request.due_date is not None:
            update_data["due_date"] = request.due_date.isoformat()
        if request.tax_rate is not None:
            update_data["tax_rate"] = str(request.tax_rate)
        if request.status is not None:
            update_data["status"] = request.status.value

        invoice_date = request.invoice_date if request.invoice_date else datetime.fromisoformat(existing_invoice["invoice_date"]).date()
        due_date = request.due_date if request.due_date else datetime.fromisoformat(existing_invoice["due_date"]).date()
        
        if due_date < invoice_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be before invoice date"
            )
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = supabase.table("invoices")\
                .update(update_data)\
                .eq("id", str(invoice_id))\
                .eq("user_id", current_user["id"])\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invoice not found"
                )

        if request.line_items is not None:

            if not request.line_items or len(request.line_items) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one line item is required"
                )

            supabase.table("line_items")\
                .delete()\
                .eq("invoice_id", str(invoice_id))\
                .execute()

            line_items_data = [
                {
                    "invoice_id": str(invoice_id),
                    "description": item.description,
                    "quantity": str(item.quantity),
                    "unit_rate": str(item.unit_rate)
                }
                for item in request.line_items
            ]
            supabase.table("line_items").insert(line_items_data).execute()
        
        return await get_invoice(invoice_id, current_user, supabase)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Delete an invoice."""
    try:

        response = supabase.table("invoices")\
            .delete()\
            .eq("id", str(invoice_id))\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def mark_invoice_sent(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Mark an invoice as sent."""
    return await _update_invoice_status(invoice_id, InvoiceStatus.SENT, "sent_date", current_user, supabase)

@router.post("/{invoice_id}/pay", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Mark an invoice as paid."""
    return await _update_invoice_status(invoice_id, InvoiceStatus.PAID, "paid_date", current_user, supabase)

async def _update_invoice_status(
    invoice_id: UUID,
    new_status: InvoiceStatus,
    date_field: str,
    current_user: dict,
    supabase: Client
) -> dict:
    """Helper to update invoice status."""
    update_data = {
        "status": new_status.value,
        date_field: datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    response = supabase.table("invoices").update(update_data).eq("id", str(invoice_id)).eq("user_id", current_user["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return await get_invoice(invoice_id, current_user, supabase)

@router.get("/{invoice_id}/pdf")
async def export_invoice_pdf(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_authenticated_supabase)
):
    """Export an invoice as a PDF document."""
    try:

        response = supabase.table("invoices")\
            .select("*, line_items(*), clients(*)")\
            .eq("id", str(invoice_id))\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        invoice_data = response.data[0]

        invoice = _convert_to_domain_model(invoice_data)

        pdf_service = PDFExportService()
        pdf_bytes = pdf_service.export_invoice(invoice)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def _convert_to_domain_model(invoice_data: dict) -> Invoice:
    """Convert database invoice data to domain model."""

    line_items = [
        LineItem(
            id=UUID(item["id"]),
            invoiceId=UUID(item["invoice_id"]),
            description=item["description"],
            quantity=Decimal(str(item["quantity"])),
            unitRate=Decimal(str(item["unit_rate"]))
        )
        for item in invoice_data.get("line_items", [])
    ]

    client_data = invoice_data.get("clients")
    client = None
    if client_data:
        client = ClientModel(
            id=UUID(client_data["id"]),
            userId=UUID(client_data["user_id"]),
            name=client_data["name"],
            email=client_data["email"],
            street=client_data["street"],
            city=client_data["city"],
            state=client_data["state"],
            zipCode=client_data["zip_code"],
            country=client_data["country"],
            phone=client_data["phone"]
        )

    invoice_date = datetime.fromisoformat(invoice_data["invoice_date"]).date() if isinstance(invoice_data["invoice_date"], str) else invoice_data["invoice_date"]
    due_date = datetime.fromisoformat(invoice_data["due_date"]).date() if isinstance(invoice_data["due_date"], str) else invoice_data["due_date"]

    invoice = Invoice(
        id=UUID(invoice_data["id"]),
        userId=UUID(invoice_data["user_id"]),
        clientId=UUID(invoice_data["client_id"]),
        invoiceNumber=invoice_data["invoice_number"],
        invoiceDate=invoice_date,
        dueDate=due_date,
        taxRate=Decimal(str(invoice_data["tax_rate"])),
        status=InvoiceStatus(invoice_data["status"]),
        sentDate=datetime.fromisoformat(invoice_data["sent_date"]) if invoice_data.get("sent_date") else None,
        paidDate=datetime.fromisoformat(invoice_data["paid_date"]) if invoice_data.get("paid_date") else None,
        lineItems=line_items,
        client=client
    )
    
    return invoice

def _transform_invoice_response(invoice_data: dict) -> dict:
    """Transform invoice data to include calculations and proper structure."""

    line_items = invoice_data.get("line_items", [])

    subtotal = Decimal("0")
    for item in line_items:
        quantity = Decimal(str(item["quantity"]))
        unit_rate = Decimal(str(item["unit_rate"]))
        subtotal += quantity * unit_rate
    
    tax_rate = Decimal(str(invoice_data["tax_rate"]))
    tax = subtotal * (tax_rate / Decimal("100"))
    total = subtotal + tax

    client_data = invoice_data.get("clients")
    client = None
    if client_data:
        client = ClientSummary(
            id=client_data["id"],
            name=client_data["name"],
            email=client_data["email"],
            street=client_data["street"],
            city=client_data["city"],
            state=client_data["state"],
            zipCode=client_data["zip_code"],
            country=client_data["country"],
            phone=client_data["phone"]
        )

    return {
        "id": invoice_data["id"],
        "userId": invoice_data["user_id"],
        "clientId": invoice_data["client_id"],
        "invoiceNumber": invoice_data["invoice_number"],
        "invoiceDate": invoice_data["invoice_date"],
        "dueDate": invoice_data["due_date"],
        "taxRate": str(invoice_data["tax_rate"]),
        "status": invoice_data["status"],
        "sentDate": invoice_data.get("sent_date"),
        "paidDate": invoice_data.get("paid_date"),
        "createdAt": invoice_data["created_at"],
        "updatedAt": invoice_data["updated_at"],
        "lineItems": [
            {
                "id": item["id"],
                "invoiceId": item["invoice_id"],
                "description": item["description"],
                "quantity": str(item["quantity"]),
                "unitRate": str(item["unit_rate"])
            }
            for item in line_items
        ],
        "client": client,
        "subtotal": str(subtotal),
        "tax": str(tax),
        "total": str(total)
    }
