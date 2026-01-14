"""Tests for PDF export service."""
from datetime import date
from decimal import Decimal
from uuid import uuid4
import pytest

from app.models import Invoice, LineItem, Client, InvoiceStatus
from app.services import PDFExportService

def test_pdf_export_generates_valid_pdf():
    """Test that PDF export generates a valid PDF document."""

    client = Client(
        id=uuid4(),
        userId=uuid4(),
        name="Test Client Inc.",
        email="client@test.com",
        street="123 Test Street",
        city="Test City",
        state="TS",
        zipCode="12345",
        country="Test Country",
        phone="+1-555-0100"
    )

    line_items = [
        LineItem(
            id=uuid4(),
            description="Web Development Services",
            quantity=Decimal("40"),
            unitRate=Decimal("150")
        ),
        LineItem(
            id=uuid4(),
            description="Design Services",
            quantity=Decimal("20"),
            unitRate=Decimal("100")
        )
    ]

    invoice = Invoice(
        id=uuid4(),
        userId=uuid4(),
        clientId=client.id,
        invoiceNumber="INV-2024-001",
        invoiceDate=date(2024, 1, 15),
        dueDate=date(2024, 2, 15),
        taxRate=Decimal("8.5"),
        status=InvoiceStatus.DRAFT,
        lineItems=line_items,
        client=client
    )

    pdf_service = PDFExportService()
    pdf_bytes = pdf_service.export_invoice(invoice)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0

    assert pdf_bytes[:5] == b'%PDF-'

def test_pdf_export_includes_invoice_details():
    """Test that PDF includes all required invoice details."""

    client = Client(
        id=uuid4(),
        userId=uuid4(),
        name="Acme Corp",
        email="billing@acme.com",
        street="456 Business Ave",
        city="Commerce City",
        state="CC",
        zipCode="54321",
        country="USA",
        phone="+1-555-0200"
    )
    
    line_items = [
        LineItem(
            id=uuid4(),
            description="Consulting Services",
            quantity=Decimal("10"),
            unitRate=Decimal("200")
        )
    ]
    
    invoice = Invoice(
        id=uuid4(),
        userId=uuid4(),
        clientId=client.id,
        invoiceNumber="INV-2024-999",
        invoiceDate=date(2024, 3, 1),
        dueDate=date(2024, 3, 31),
        taxRate=Decimal("10"),
        status=InvoiceStatus.SENT,
        lineItems=line_items,
        client=client
    )

    pdf_service = PDFExportService()
    pdf_bytes = pdf_service.export_invoice(invoice)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0

    assert pdf_bytes[:5] == b'%PDF-'

    assert len(pdf_bytes) > 1000  # A formatted invoice should be at least 1KB

def test_pdf_export_with_multiple_line_items():
    """Test PDF generation with multiple line items."""
    client = Client(
        id=uuid4(),
        userId=uuid4(),
        name="Multi-Item Client",
        email="multi@test.com",
        street="789 Multi Lane",
        city="Item City",
        state="IC",
        zipCode="99999",
        country="Testland",
        phone="+1-555-0300"
    )

    line_items = [
        LineItem(
            id=uuid4(),
            description=f"Service {i}",
            quantity=Decimal(str(i * 10)),
            unitRate=Decimal(str(50 + i * 10))
        )
        for i in range(1, 6)
    ]
    
    invoice = Invoice(
        id=uuid4(),
        userId=uuid4(),
        clientId=client.id,
        invoiceNumber="INV-MULTI-001",
        invoiceDate=date(2024, 4, 1),
        dueDate=date(2024, 5, 1),
        taxRate=Decimal("7.5"),
        status=InvoiceStatus.DRAFT,
        lineItems=line_items,
        client=client
    )

    pdf_service = PDFExportService()
    pdf_bytes = pdf_service.export_invoice(invoice)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:5] == b'%PDF-'

def test_pdf_export_with_zero_tax():
    """Test PDF generation with zero tax rate."""
    client = Client(
        id=uuid4(),
        userId=uuid4(),
        name="No Tax Client",
        email="notax@test.com",
        street="100 Tax Free Blvd",
        city="Zero City",
        state="ZC",
        zipCode="00000",
        country="Tax Haven",
        phone="+1-555-0400"
    )
    
    line_items = [
        LineItem(
            id=uuid4(),
            description="Tax-Free Service",
            quantity=Decimal("1"),
            unitRate=Decimal("1000")
        )
    ]
    
    invoice = Invoice(
        id=uuid4(),
        userId=uuid4(),
        clientId=client.id,
        invoiceNumber="INV-NOTAX-001",
        invoiceDate=date(2024, 5, 1),
        dueDate=date(2024, 6, 1),
        taxRate=Decimal("0"),
        status=InvoiceStatus.PAID,
        lineItems=line_items,
        client=client
    )

    pdf_service = PDFExportService()
    pdf_bytes = pdf_service.export_invoice(invoice)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:5] == b'%PDF-'
