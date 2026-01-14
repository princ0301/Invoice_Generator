"""Property-based tests for Invoice Generator."""
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite

from app.models import Client, LineItem, Invoice, InvoiceStatus

@composite
def valid_email(draw):
    """Generate valid email addresses."""
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=1,
        max_size=20
    ))
    domain = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll',)),
        min_size=1,
        max_size=20
    ))
    tld = draw(st.sampled_from(['com', 'org', 'net', 'io', 'co']))
    return f"{username}@{domain}.{tld}"

@composite
def valid_client(draw):
    """Generate valid Client instances."""
    return Client(
        userId=uuid4(),
        name=draw(st.text(min_size=1, max_size=100)),
        email=draw(valid_email()),
        street=draw(st.text(min_size=1, max_size=100)),
        city=draw(st.text(min_size=1, max_size=50)),
        state=draw(st.text(min_size=1, max_size=50)),
        zipCode=draw(st.text(min_size=1, max_size=20)),
        country=draw(st.text(min_size=1, max_size=50)),
        phone=draw(st.text(min_size=1, max_size=30))
    )

@composite
def valid_line_item(draw):
    """Generate valid LineItem instances."""
    quantity = draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("10000"),
        places=2
    ))
    unit_rate = draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("100000"),
        places=2
    ))
    
    return LineItem(
        description=draw(st.text(min_size=1, max_size=200)),
        quantity=quantity,
        unitRate=unit_rate
    )

@composite
def valid_invoice(draw, min_items=1, max_items=50):
    """Generate valid Invoice instances."""
    invoice_date = draw(st.dates(
        min_value=date(2020, 1, 1),
        max_value=date(2030, 12, 31)
    ))
    days_until_due = draw(st.integers(min_value=1, max_value=365))
    due_date = invoice_date + timedelta(days=days_until_due)
    
    num_items = draw(st.integers(min_value=min_items, max_value=max_items))
    line_items = [draw(valid_line_item()) for _ in range(num_items)]
    
    tax_rate = draw(st.decimals(
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        places=2
    ))
    
    return Invoice(
        userId=uuid4(),
        clientId=uuid4(),
        invoiceNumber=draw(st.text(min_size=1, max_size=50)),
        invoiceDate=invoice_date,
        dueDate=due_date,
        taxRate=tax_rate,
        lineItems=line_items
    )

@given(st.lists(st.text(min_size=1, max_size=50), min_size=2, max_size=100, unique=True))
def test_property_invoice_number_uniqueness(invoice_numbers):
    """Property 1: Invoice Number Uniqueness - Validates: Requirements 1.1"""
    invoices = []
    for inv_num in invoice_numbers:
        line_item = LineItem(
            description="Test Item",
            quantity=Decimal("1"),
            unitRate=Decimal("100")
        )
        invoice = Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber=inv_num,
            invoiceDate=date(2024, 1, 1),
            dueDate=date(2024, 2, 1),
            lineItems=[line_item]
        )
        invoices.append(invoice)
    
    actual_numbers = [inv.invoice_number for inv in invoices]
    assert len(actual_numbers) == len(set(actual_numbers))

@given(valid_invoice())
@settings(max_examples=100)
def test_property_invoice_calculation_correctness(invoice):
    """
    Property 2: Invoice Calculation Correctness
    
    For any invoice with line items and a tax rate, the following must hold:
    - Subtotal equals the sum of all line item amounts (quantity × unitRate)
    - Tax equals subtotal × taxRate
    - Total equals subtotal + tax
    
    Validates: Requirements 1.2, 1.3, 1.4
    """

    expected_subtotal = sum(
        item.quantity * item.unit_rate for item in invoice.line_items
    )

    expected_tax = expected_subtotal * (invoice.tax_rate / Decimal("100"))

    expected_total = expected_subtotal + expected_tax

    assert invoice.calculate_subtotal() == expected_subtotal
    assert invoice.calculate_tax() == expected_tax
    assert invoice.calculate_total() == expected_total

@given(valid_line_item())
@settings(max_examples=100)
def test_property_line_item_amount_calculation(line_item):
    """
    Property 9: Line Item Amount Calculation
    
    For any line item with quantity and unit rate, the calculated amount 
    should equal quantity × unitRate.
    
    Validates: Requirements 3.2
    """
    expected_amount = line_item.quantity * line_item.unit_rate
    assert line_item.calculate_amount() == expected_amount

@given(valid_invoice(min_items=2, max_items=10), valid_line_item())
@settings(max_examples=100)
def test_property_invoice_recalculation_on_add(invoice, new_item):
    """
    Property 10: Invoice Recalculation on Line Item Changes (Add)
    
    For any invoice, when line items are added, the invoice totals 
    (subtotal, tax, total) should be recalculated to reflect the current 
    line items.
    
    Validates: Requirements 3.3
    """

    subtotal_before = invoice.calculate_subtotal()
    tax_before = invoice.calculate_tax()
    total_before = invoice.calculate_total()

    invoice.add_line_item(new_item)

    subtotal_after = invoice.calculate_subtotal()
    tax_after = invoice.calculate_tax()
    total_after = invoice.calculate_total()

    new_item_amount = new_item.calculate_amount()
    expected_subtotal = subtotal_before + new_item_amount
    expected_tax = expected_subtotal * (invoice.tax_rate / Decimal("100"))
    expected_total = expected_subtotal + expected_tax
    
    assert subtotal_after == expected_subtotal
    assert tax_after == expected_tax
    assert total_after == expected_total

@given(valid_invoice(min_items=2, max_items=10))
@settings(max_examples=100)
def test_property_invoice_recalculation_on_remove(invoice):
    """
    Property 10: Invoice Recalculation on Line Item Changes (Remove)
    
    For any invoice, when line items are removed, the invoice totals 
    (subtotal, tax, total) should be recalculated to reflect the current 
    line items.
    
    Validates: Requirements 3.4
    """

    assume(len(invoice.line_items) >= 2)

    item_to_remove = invoice.line_items[0]
    removed_amount = item_to_remove.calculate_amount()

    subtotal_before = invoice.calculate_subtotal()

    invoice.remove_line_item(item_to_remove.id)

    subtotal_after = invoice.calculate_subtotal()
    tax_after = invoice.calculate_tax()
    total_after = invoice.calculate_total()

    expected_subtotal = subtotal_before - removed_amount
    expected_tax = expected_subtotal * (invoice.tax_rate / Decimal("100"))
    expected_total = expected_subtotal + expected_tax
    
    assert subtotal_after == expected_subtotal
    assert tax_after == expected_tax
    assert total_after == expected_total

@given(valid_invoice())
@settings(max_examples=100)
def test_property_initial_invoice_status(invoice):
    """
    Property 13: Initial Invoice Status
    
    For any newly created invoice, the initial status should be "draft".
    
    Validates: Requirements 5.1
    """
    assert invoice.status == InvoiceStatus.DRAFT

@given(valid_invoice())
@settings(max_examples=100)
def test_property_status_transition_to_sent(invoice):
    """
    Property 14: Status Transition with Date Recording (Sent)
    
    For any invoice, when marking it as sent, both the status should update 
    and the sentDate should be recorded.
    
    Validates: Requirements 5.2
    """

    assert invoice.status == InvoiceStatus.DRAFT
    assert invoice.sent_date is None

    invoice.update_status(InvoiceStatus.SENT)

    assert invoice.status == InvoiceStatus.SENT
    assert invoice.sent_date is not None

@given(valid_invoice())
@settings(max_examples=100)
def test_property_status_transition_to_paid(invoice):
    """
    Property 14: Status Transition with Date Recording (Paid)
    
    For any invoice, when marking it as paid, both the status should update 
    and the paidDate should be recorded.
    
    Validates: Requirements 5.3
    """

    assert invoice.paid_date is None

    invoice.update_status(InvoiceStatus.PAID)

    assert invoice.status == InvoiceStatus.PAID
    assert invoice.paid_date is not None

@given(
    st.decimals(min_value=Decimal("-10000"), max_value=Decimal("-0.01"), places=2),
    st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10000"), places=2)
)
@settings(max_examples=100)
def test_property_negative_quantity_rejection(negative_quantity, positive_rate):
    """
    Property 20: Negative Value Rejection (Quantity)
    
    For any line item with negative quantity, the system should reject 
    the input and return a validation error.
    
    Validates: Requirements 7.1
    """
    with pytest.raises(Exception):
        LineItem(
            description="Test Item",
            quantity=negative_quantity,
            unitRate=positive_rate
        )

@given(
    st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10000"), places=2),
    st.decimals(min_value=Decimal("-10000"), max_value=Decimal("-0.01"), places=2)
)
@settings(max_examples=100)
def test_property_negative_rate_rejection(positive_quantity, negative_rate):
    """
    Property 20: Negative Value Rejection (Rate)
    
    For any line item with negative unit rate, the system should reject 
    the input and return a validation error.
    
    Validates: Requirements 7.1
    """
    with pytest.raises(Exception):
        LineItem(
            description="Test Item",
            quantity=positive_quantity,
            unitRate=negative_rate
        )

@given(
    st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)),
    st.integers(min_value=1, max_value=365)
)
@settings(max_examples=100)
def test_property_date_range_validation(invoice_date, days_before):
    """
    Property 21: Date Range Validation
    
    For any invoice where the due date is before the invoice date, the 
    system should reject the input and return a validation error.
    
    Validates: Requirements 7.2
    """

    due_date = invoice_date - timedelta(days=days_before)
    
    line_item = LineItem(
        description="Test Item",
        quantity=Decimal("1"),
        unitRate=Decimal("100")
    )
    
    with pytest.raises(ValueError, match="Due date cannot be before invoice date"):
        Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=invoice_date,
            dueDate=due_date,
            lineItems=[line_item]
        )

@given(st.text(min_size=1, max_size=50).filter(lambda x: '@' not in x))
@settings(max_examples=100)
def test_property_email_format_validation(invalid_email):
    """
    Property 22: Email Format Validation
    
    For any client with an invalid email format, the system should reject 
    the input and return a validation error.
    
    Validates: Requirements 7.4
    """
    with pytest.raises(Exception):
        Client(
            userId=uuid4(),
            name="Test Client",
            email=invalid_email,
            street="123 Main St",
            city="Test City",
            state="TS",
            zipCode="12345",
            country="Test Country",
            phone="+1-555-0100"
        )

def test_property_required_fields_no_line_items():
    """
    Property 3: Required Fields Validation (Line Items)
    
    For any invoice creation attempt, if line items are missing, the system 
    should reject the creation.
    
    Validates: Requirements 1.5
    """
    with pytest.raises(ValueError, match="At least one line item is required"):
        Invoice(
            userId=uuid4(),
            clientId=uuid4(),
            invoiceNumber="INV-001",
            invoiceDate=date(2024, 1, 1),
            dueDate=date(2024, 2, 1),
            lineItems=[]
        )

def test_property_line_item_required_description():
    """
    Property 8: Line Item Required Fields (Description)
    
    For any line item creation attempt, if description is missing, the 
    system should reject the creation.
    
    Validates: Requirements 3.1
    """
    with pytest.raises(Exception):
        LineItem(
            description="",
            quantity=Decimal("1"),
            unitRate=Decimal("100")
        )

@given(valid_invoice())
@settings(max_examples=100)
def test_property_zero_tax_rate(invoice):
    """
    Test that invoices with zero tax rate calculate correctly.
    
    For any invoice with tax rate of 0, tax should be 0 and total should 
    equal subtotal.
    """

    invoice.tax_rate = Decimal("0")
    
    subtotal = invoice.calculate_subtotal()
    tax = invoice.calculate_tax()
    total = invoice.calculate_total()
    
    assert tax == Decimal("0")
    assert total == subtotal

@given(valid_invoice(min_items=1, max_items=50))
@settings(max_examples=100)
def test_property_many_line_items(invoice):
    """
    Test that invoices can handle up to 50 line items correctly.
    
    For any invoice with multiple line items, calculations should remain 
    accurate regardless of the number of items.
    
    Validates: Requirements 3.5
    """

    subtotal = invoice.calculate_subtotal()
    tax = invoice.calculate_tax()
    total = invoice.calculate_total()

    assert total == subtotal + tax
    assert len(invoice.line_items) <= 50
