"""End-to-end integration tests for Invoice Generator.

These tests validate the complete workflow from authentication through
invoice creation, management, and PDF export.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthenticationFlow:
    """Test authentication workflow."""
    
    def test_register_and_login_flow(self):
        """Test complete registration and login flow."""
        pytest.skip("Requires valid Supabase configuration")

class TestClientManagementFlow:
    """Test client management workflow."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""

        pytest.skip("Requires Supabase test user setup")
    
    def test_create_list_update_delete_client(self, auth_token):
        """Test complete client CRUD workflow."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "Test Client Corp",
            "email": "client@testcorp.com",
            "street": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "zipCode": "12345",
            "country": "Testland",
            "phone": "+1-555-0100"
        }
        
        create_response = client.post("/api/clients", json=client_data, headers=headers)
        assert create_response.status_code == 201
        created_client = create_response.json()
        client_id = created_client["id"]

        list_response = client.get("/api/clients", headers=headers)
        assert list_response.status_code == 200
        clients = list_response.json()
        assert any(c["id"] == client_id for c in clients)

        get_response = client.get(f"/api/clients/{client_id}", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["id"] == client_id

        update_data = {"name": "Updated Client Corp"}
        update_response = client.put(
            f"/api/clients/{client_id}",
            json=update_data,
            headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Client Corp"

        delete_response = client.delete(f"/api/clients/{client_id}", headers=headers)
        assert delete_response.status_code == 204

class TestInvoiceManagementFlow:
    """Test invoice management workflow."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        pytest.skip("Requires Supabase test user setup")
    
    @pytest.fixture
    def test_client_id(self, auth_token):
        """Create a test client and return its ID."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        client_data = {
            "name": "Invoice Test Client",
            "email": "invoice@test.com",
            "street": "456 Invoice St",
            "city": "Invoice City",
            "state": "IC",
            "zipCode": "54321",
            "country": "Testland",
            "phone": "+1-555-0200"
        }
        
        response = client.post("/api/clients", json=client_data, headers=headers)
        return response.json()["id"]
    
    def test_create_invoice_with_line_items(self, auth_token, test_client_id):
        """Test creating an invoice with line items."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        invoice_data = {
            "clientId": test_client_id,
            "invoiceNumber": f"INV-TEST-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "8.5",
            "lineItems": [
                {
                    "description": "Web Development",
                    "quantity": "40",
                    "unitRate": "150"
                },
                {
                    "description": "Design Services",
                    "quantity": "20",
                    "unitRate": "100"
                }
            ]
        }
        
        response = client.post("/api/invoices", json=invoice_data, headers=headers)
        assert response.status_code == 201
        
        invoice = response.json()
        assert invoice["invoiceNumber"] == invoice_data["invoiceNumber"]
        assert len(invoice["lineItems"]) == 2
        assert invoice["status"] == "draft"

        assert Decimal(invoice["subtotal"]) == Decimal("8000")  # 40*150 + 20*100
        assert Decimal(invoice["tax"]) == Decimal("680")  # 8000 * 0.085
        assert Decimal(invoice["total"]) == Decimal("8680")  # 8000 + 680
    
    def test_invoice_status_transitions(self, auth_token, test_client_id):
        """Test invoice status transitions from draft to sent to paid."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        invoice_data = {
            "clientId": test_client_id,
            "invoiceNumber": f"INV-STATUS-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "10",
            "lineItems": [
                {
                    "description": "Service",
                    "quantity": "1",
                    "unitRate": "1000"
                }
            ]
        }
        
        create_response = client.post("/api/invoices", json=invoice_data, headers=headers)
        invoice_id = create_response.json()["id"]

        get_response = client.get(f"/api/invoices/{invoice_id}", headers=headers)
        assert get_response.json()["status"] == "draft"

        sent_response = client.post(f"/api/invoices/{invoice_id}/send", headers=headers)
        assert sent_response.status_code == 200
        sent_invoice = sent_response.json()
        assert sent_invoice["status"] == "sent"
        assert sent_invoice["sentDate"] is not None

        paid_response = client.post(f"/api/invoices/{invoice_id}/pay", headers=headers)
        assert paid_response.status_code == 200
        paid_invoice = paid_response.json()
        assert paid_invoice["status"] == "paid"
        assert paid_invoice["paidDate"] is not None
    
    def test_update_invoice_line_items(self, auth_token, test_client_id):
        """Test updating invoice line items recalculates totals."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        invoice_data = {
            "clientId": test_client_id,
            "invoiceNumber": f"INV-UPDATE-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "10",
            "lineItems": [
                {
                    "description": "Original Service",
                    "quantity": "1",
                    "unitRate": "100"
                }
            ]
        }
        
        create_response = client.post("/api/invoices", json=invoice_data, headers=headers)
        invoice_id = create_response.json()["id"]

        update_data = {
            "lineItems": [
                {
                    "description": "Updated Service 1",
                    "quantity": "2",
                    "unitRate": "150"
                },
                {
                    "description": "Updated Service 2",
                    "quantity": "3",
                    "unitRate": "100"
                }
            ]
        }
        
        update_response = client.put(
            f"/api/invoices/{invoice_id}",
            json=update_data,
            headers=headers
        )
        
        assert update_response.status_code == 200
        updated_invoice = update_response.json()

        assert len(updated_invoice["lineItems"]) == 2
        assert Decimal(updated_invoice["subtotal"]) == Decimal("600")  # 2*150 + 3*100
        assert Decimal(updated_invoice["tax"]) == Decimal("60")  # 600 * 0.10
        assert Decimal(updated_invoice["total"]) == Decimal("660")  # 600 + 60

class TestPDFExportFlow:
    """Test PDF export workflow."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        pytest.skip("Requires Supabase test user setup")
    
    @pytest.fixture
    def test_invoice_id(self, auth_token):
        """Create a test invoice and return its ID."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "PDF Test Client",
            "email": "pdf@test.com",
            "street": "789 PDF Lane",
            "city": "PDF City",
            "state": "PC",
            "zipCode": "99999",
            "country": "Testland",
            "phone": "+1-555-0300"
        }
        client_response = client.post("/api/clients", json=client_data, headers=headers)
        client_id = client_response.json()["id"]

        invoice_data = {
            "clientId": client_id,
            "invoiceNumber": f"INV-PDF-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "8.5",
            "lineItems": [
                {
                    "description": "PDF Test Service",
                    "quantity": "10",
                    "unitRate": "200"
                }
            ]
        }
        invoice_response = client.post("/api/invoices", json=invoice_data, headers=headers)
        return invoice_response.json()["id"]
    
    def test_export_invoice_as_pdf(self, auth_token, test_invoice_id):
        """Test exporting an invoice as PDF."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get(f"/api/invoices/{test_invoice_id}/pdf", headers=headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]

        pdf_bytes = response.content
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b'%PDF-'

class TestClientDeletionProtection:
    """Test that clients with invoices cannot be deleted."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        pytest.skip("Requires Supabase test user setup")
    
    def test_cannot_delete_client_with_invoices(self, auth_token):
        """Test that deleting a client with invoices is prevented."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "Protected Client",
            "email": "protected@test.com",
            "street": "100 Protected St",
            "city": "Protected City",
            "state": "PC",
            "zipCode": "00000",
            "country": "Testland",
            "phone": "+1-555-0400"
        }
        client_response = client.post("/api/clients", json=client_data, headers=headers)
        client_id = client_response.json()["id"]

        invoice_data = {
            "clientId": client_id,
            "invoiceNumber": f"INV-PROTECT-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "0",
            "lineItems": [
                {
                    "description": "Service",
                    "quantity": "1",
                    "unitRate": "100"
                }
            ]
        }
        client.post("/api/invoices", json=invoice_data, headers=headers)

        delete_response = client.delete(f"/api/clients/{client_id}", headers=headers)

        assert delete_response.status_code == 400
        assert "associated invoices" in delete_response.json()["detail"].lower()

class TestValidationErrors:
    """Test validation error handling."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        pytest.skip("Requires Supabase test user setup")
    
    def test_invoice_due_date_before_invoice_date(self, auth_token):
        """Test that due date before invoice date is rejected."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "Validation Test Client",
            "email": "validation@test.com",
            "street": "123 Validation St",
            "city": "Validation City",
            "state": "VC",
            "zipCode": "11111",
            "country": "Testland",
            "phone": "+1-555-0500"
        }
        client_response = client.post("/api/clients", json=client_data, headers=headers)
        client_id = client_response.json()["id"]

        invoice_data = {
            "clientId": client_id,
            "invoiceNumber": f"INV-INVALID-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() - timedelta(days=1)).isoformat(),  # Before invoice date
            "taxRate": "0",
            "lineItems": [
                {
                    "description": "Service",
                    "quantity": "1",
                    "unitRate": "100"
                }
            ]
        }
        
        response = client.post("/api/invoices", json=invoice_data, headers=headers)
        
        assert response.status_code == 400
        assert "due date" in response.json()["detail"].lower()
    
    def test_invoice_without_line_items(self, auth_token):
        """Test that invoice without line items is rejected."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "No Items Client",
            "email": "noitems@test.com",
            "street": "456 No Items Ave",
            "city": "No Items City",
            "state": "NI",
            "zipCode": "22222",
            "country": "Testland",
            "phone": "+1-555-0600"
        }
        client_response = client.post("/api/clients", json=client_data, headers=headers)
        client_id = client_response.json()["id"]

        invoice_data = {
            "clientId": client_id,
            "invoiceNumber": f"INV-NOITEMS-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "0",
            "lineItems": []  # Empty line items
        }
        
        response = client.post("/api/invoices", json=invoice_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_negative_line_item_values(self, auth_token):
        """Test that negative quantities and rates are rejected."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "Negative Test Client",
            "email": "negative@test.com",
            "street": "789 Negative Blvd",
            "city": "Negative City",
            "state": "NC",
            "zipCode": "33333",
            "country": "Testland",
            "phone": "+1-555-0700"
        }
        client_response = client.post("/api/clients", json=client_data, headers=headers)
        client_id = client_response.json()["id"]

        invoice_data = {
            "clientId": client_id,
            "invoiceNumber": f"INV-NEG-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "0",
            "lineItems": [
                {
                    "description": "Service",
                    "quantity": "-5",  # Negative quantity
                    "unitRate": "100"
                }
            ]
        }
        
        response = client.post("/api/invoices", json=invoice_data, headers=headers)
        assert response.status_code == 422  # Validation error

class TestInvoiceFiltering:
    """Test invoice filtering by status."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        pytest.skip("Requires Supabase test user setup")
    
    def test_filter_invoices_by_status(self, auth_token):
        """Test filtering invoices by status."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        client_data = {
            "name": "Filter Test Client",
            "email": "filter@test.com",
            "street": "100 Filter St",
            "city": "Filter City",
            "state": "FC",
            "zipCode": "44444",
            "country": "Testland",
            "phone": "+1-555-0800"
        }
        client_response = client.post("/api/clients", json=client_data, headers=headers)
        client_id = client_response.json()["id"]

        draft_invoice = {
            "clientId": client_id,
            "invoiceNumber": f"INV-DRAFT-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "0",
            "lineItems": [{"description": "Service", "quantity": "1", "unitRate": "100"}]
        }
        client.post("/api/invoices", json=draft_invoice, headers=headers)

        sent_invoice_data = {
            "clientId": client_id,
            "invoiceNumber": f"INV-SENT-{uuid4().hex[:8]}",
            "invoiceDate": date.today().isoformat(),
            "dueDate": (date.today() + timedelta(days=30)).isoformat(),
            "taxRate": "0",
            "lineItems": [{"description": "Service", "quantity": "1", "unitRate": "100"}]
        }
        sent_response = client.post("/api/invoices", json=sent_invoice_data, headers=headers)
        sent_invoice_id = sent_response.json()["id"]
        client.post(f"/api/invoices/{sent_invoice_id}/send", headers=headers)

        draft_response = client.get("/api/invoices?status_filter=draft", headers=headers)
        assert draft_response.status_code == 200
        draft_invoices = draft_response.json()
        assert all(inv["status"] == "draft" for inv in draft_invoices)

        sent_response = client.get("/api/invoices?status_filter=sent", headers=headers)
        assert sent_response.status_code == 200
        sent_invoices = sent_response.json()
        assert all(inv["status"] == "sent" for inv in sent_invoices)
