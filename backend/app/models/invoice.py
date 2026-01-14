"""Invoice domain model with validation and calculation."""
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .line_item import LineItem
from .client import Client

class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"

class Invoice(BaseModel):
    """Invoice domain model with calculation and validation logic."""
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "userId": "123e4567-e89b-12d3-a456-426614174000",
                "clientId": "223e4567-e89b-12d3-a456-426614174000",
                "invoiceNumber": "INV-2024-001",
                "invoiceDate": "2024-01-15",
                "dueDate": "2024-02-15",
                "taxRate": "8.5",
                "status": "draft",
                "lineItems": [
                    {
                        "description": "Web Development",
                        "quantity": "40",
                        "unitRate": "150"
                    }
                ]
            }
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(..., alias="userId")
    client_id: UUID = Field(..., alias="clientId")
    invoice_number: str = Field(..., min_length=1, alias="invoiceNumber")
    invoice_date: date = Field(..., alias="invoiceDate")
    due_date: date = Field(..., alias="dueDate")
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, alias="taxRate")
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT)
    sent_date: Optional[datetime] = Field(default=None, alias="sentDate")
    paid_date: Optional[datetime] = Field(default=None, alias="paidDate")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")

    line_items: List[LineItem] = Field(default_factory=list, alias="lineItems")
    client: Optional[Client] = None

    @field_validator('line_items')
    @classmethod
    def validate_line_items_not_empty(cls, v: List[LineItem]) -> List[LineItem]:
        """Validate that at least one line item is present."""
        if not v or len(v) == 0:
            raise ValueError('At least one line item is required')
        return v

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that due_date is not before invoice_date."""
        if self.due_date < self.invoice_date:
            raise ValueError('Due date cannot be before invoice date')
        return self

    def calculate_subtotal(self) -> Decimal:
        """Calculate the subtotal by summing all line item amounts."""
        return sum(
            (item.calculate_amount() for item in self.line_items),
            start=Decimal("0")
        )

    def calculate_tax(self) -> Decimal:
        """Calculate tax based on subtotal and tax rate."""
        subtotal = self.calculate_subtotal()
        return subtotal * (self.tax_rate / Decimal("100"))

    def calculate_total(self) -> Decimal:
        """Calculate the total amount (subtotal + tax)."""
        return self.calculate_subtotal() + self.calculate_tax()

    def add_line_item(self, item: LineItem) -> None:
        """Add a line item to the invoice."""
        self.line_items.append(item)
        self.updated_at = datetime.now(timezone.utc)

    def remove_line_item(self, item_id: UUID) -> None:
        """Remove a line item from the invoice by ID."""
        self.line_items = [item for item in self.line_items if item.id != item_id]
        self.updated_at = datetime.now(timezone.utc)

    def update_status(self, new_status: InvoiceStatus) -> None:
        """Update the invoice status and set corresponding date fields."""
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        
        if new_status == InvoiceStatus.SENT and self.sent_date is None:
            self.sent_date = datetime.now(timezone.utc)
        elif new_status == InvoiceStatus.PAID and self.paid_date is None:
            self.paid_date = datetime.now(timezone.utc)

    def check_overdue(self) -> None:
        """Check if invoice is overdue and update status if necessary."""
        if self.status == InvoiceStatus.SENT and date.today() > self.due_date:
            self.status = InvoiceStatus.OVERDUE
            self.updated_at = datetime.now(timezone.utc)
