"""Tests for domain models."""
import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from app.models import Client, LineItem, Invoice, InvoiceStatus

class TestClient:
    """Tests for Client model."""

    def test_client_creation(self):
        """Test creating a valid client."""
        user_id = uuid4()
        client = Client(
            userId=user_id,
            name="Acme Corp",
            email="test@acme.com",
            street="123 Main St",
            city="San Francisco",
            state="CA",
            zipCode="94102",
            country="USA",
            phone="+1-555-0100"
        )
        assert client.name == "Acme Corp"
        assert client.email == "test@acme.com"
        assert client.user_id == user_id

    def test_client_invalid_email(self):
        """Test that invalid email is rejected."""
        with pytest.raises(Exception):
            Client(
                userId=uuid4(),
                name="Acme Corp",
                email="invalid-email",
                street="123 Main St",
                city="San Francisco",
                state="CA",
                zipCode="94102",
                country="USA",
                phone="+1-555-0100"
            )

    def test_client_get_address(self):
        """Test getting address from client."""
        client = Client(
            userId=uuid4(),
            name="Acme Corp",
            email="test@acme.com",
            street="123 Main St",
            city="San Francisco",
            state="CA",
            zipCode="94102",
            country="USA",
            phone="+1-555-0100"
        )
        address = client.get_address()
        assert address.street == "123 Main St"
        assert address.city == "San Francisco"
        assert address.zip_code == "94102"

class TestLineItem:
    """Tests for LineItem model."""

    def test_line_item_creation(self):
        """Test creating a valid line item."""
        item = LineItem(
            description="Web Development",
            quantity=Decimal("40"),
            unitRate=Decimal("150")
        )
        assert item.description == "Web Development"
        assert item.quantity == Decimal("40")
        assert item.unit_rate == Decimal("150")

    def test_line_item_calculate_amount(self):
        """Test line item amount calculation."""
        item = LineItem(
            description="Web Development",
            quantity=Decimal("40"),
            unitRate=Decimal("150")
        )
        assert item.calculate_amount() == Decimal("6000")

    def test_line_item_negative_quantity(self):
        """Test that negative quantity is rejected."""
        with pytest.raises(Exception):
            LineItem(
                description="Web Development",
                quantity=Decimal("-40"),
                unitRate=Decimal("150")
            )

    def test_line_item_negative_rate(self):
        """Test that negative unit rate is rejected."""
        with pytest.raises(Exception):
            LineItem(
                description="Web Development",
                quantity=Decimal("40"),
                unitRate=Decimal("-150")
            )

    def test_line_item_zero_quantity(self):
        """Test that zero quantity is rejected."""
        with pytest.raises(Exception):
            LineItem(
                description="Web Development",
                quantity=Decimal("0"),
                unitRate=Decimal("150")
            )

class TestInvoice:
    """Tests for Invoice model."""

    def test_invoice_creation(self):
        """Test creating a valid invoice."""
        user_id = uuid4()
        client_id = uuid4()
        line_items = [
            LineItem(
                description="Web Development",
                quantity=Decimal("40"),
                unitRate=Decimal("150")
            )
        ]
        
        invoice = Invoice(
            userId=user_id,
            clientId=client_id,
            invoiceNumber="INV-2024-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            taxRate=Decimal("8.5"),
            lineItems=line_items
        )
        
        assert invoice.invoice_number == "INV-2024-001"
        assert invoice.status == InvoiceStatus.DRAFT
        assert len(invoice.line_items) == 1

    def test_invoice_calculate_subtotal(self):
        """Test invoice subtotal calculation."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("2"), unitRate=Decimal("100")),
            LineItem(description="Item 2", quantity=Decimal("3"), unitRate=Decimal("50"))
        ]
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            lineItems=line_items
        )
        
        assert invoice.calculate_subtotal() == Decimal("350")

    def test_invoice_calculate_tax(self):
        """Test invoice tax calculation."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("10"), unitRate=Decimal("100"))
        ]
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            taxRate=Decimal("10"),
            lineItems=line_items
        )
        
        assert invoice.calculate_tax() == Decimal("100")

    def test_invoice_calculate_total(self):
        """Test invoice total calculation."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("10"), unitRate=Decimal("100"))
        ]
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            taxRate=Decimal("10"),
            lineItems=line_items
        )
        
        assert invoice.calculate_total() == Decimal("1100")

    def test_invoice_due_date_before_invoice_date(self):
        """Test that due date before invoice date is rejected."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("1"), unitRate=Decimal("100"))
        ]
        
        with pytest.raises(Exception):
            Invoice(
                userId=uuid4(),
                clientId=uuid4(),
                invoiceNumber="INV-001",
                invoiceDate=date(2024, 2, 15),
                dueDate=date(2024, 1, 15),
                lineItems=line_items
            )

    def test_invoice_no_line_items(self):
        """Test that invoice without line items is rejected."""
        with pytest.raises(Exception):
            Invoice(
                userId=uuid4(),
                clientId=uuid4(),
                invoiceNumber="INV-001",
                invoiceDate=date(2024, 1, 15),
                dueDate=date(2024, 2, 15),
                lineItems=[]
            )

    def test_invoice_add_line_item(self):
        """Test adding a line item to an invoice."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("1"), unitRate=Decimal("100"))
        ]
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            lineItems=line_items
        )
        
        new_item = LineItem(description="Item 2", quantity=Decimal("2"), unitRate=Decimal("50"))
        invoice.add_line_item(new_item)
        
        assert len(invoice.line_items) == 2
        assert invoice.calculate_subtotal() == Decimal("200")

    def test_invoice_remove_line_item(self):
        """Test removing a line item from an invoice."""
        item1 = LineItem(description="Item 1", quantity=Decimal("1"), unitRate=Decimal("100"))
        item2 = LineItem(description="Item 2", quantity=Decimal("2"), unitRate=Decimal("50"))
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            lineItems=[item1, item2]
        )
        
        invoice.remove_line_item(item1.id)
        
        assert len(invoice.line_items) == 1
        assert invoice.calculate_subtotal() == Decimal("100")

    def test_invoice_update_status_to_sent(self):
        """Test updating invoice status to sent."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("1"), unitRate=Decimal("100"))
        ]
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            lineItems=line_items
        )
        
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.sent_date is None
        
        invoice.update_status(InvoiceStatus.SENT)
        
        assert invoice.status == InvoiceStatus.SENT
        assert invoice.sent_date is not None

    def test_invoice_update_status_to_paid(self):
        """Test updating invoice status to paid."""
        line_items = [
            LineItem(description="Item 1", quantity=Decimal("1"), unitRate=Decimal("100"))
        ]
        
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 15),
            dueDate=date(2024, 2, 15),
            lineItems=line_items
        )
        
        invoice.update_status(InvoiceStatus.PAID)
        
        assert invoice.status == InvoiceStatus.PAID
        assert invoice.paid_date is not None
