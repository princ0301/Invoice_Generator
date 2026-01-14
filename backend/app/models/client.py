"""Client domain model with validation."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class Address(BaseModel):
    """Client address information."""
    model_config = ConfigDict(populate_by_name=True)
    
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    zip_code: str = Field(..., min_length=1, alias="zipCode")
    country: str = Field(..., min_length=1)

class Client(BaseModel):
    """Client domain model representing a customer."""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "userId": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Acme Corporation",
                "email": "billing@acme.com",
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zipCode": "94102",
                "country": "USA",
                "phone": "+1-555-0100"
            }
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(..., alias="userId")
    name: str = Field(..., min_length=1)
    email: EmailStr
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    zip_code: str = Field(..., min_length=1, alias="zipCode")
    country: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")

    def get_address(self) -> Address:
        """Get the client's address as an Address object."""
        return Address(
            street=self.street,
            city=self.city,
            state=self.state,
            zipCode=self.zip_code,
            country=self.country
        )
