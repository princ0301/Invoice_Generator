"""LineItem domain model with validation and calculation."""
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator

class LineItem(BaseModel):
    """LineItem domain model representing a single invoice entry."""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "description": "Web Development Services",
                "quantity": "40.00",
                "unitRate": "150.00"
            }
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    invoice_id: Optional[UUID] = Field(default=None, alias="invoiceId")
    description: str = Field(..., min_length=1)
    quantity: Decimal = Field(..., gt=0)
    unit_rate: Decimal = Field(..., gt=0, alias="unitRate")

    @field_validator('quantity', 'unit_rate')
    @classmethod
    def validate_positive(cls, v: Decimal, info) -> Decimal:
        """Validate that quantity and unit_rate are positive numbers."""
        if v <= 0:
            raise ValueError(f'{info.field_name} must be greater than 0')
        return v

    def calculate_amount(self) -> Decimal:
        """Calculate the line item total (quantity × unit_rate)."""
        return self.quantity * self.unit_rate
