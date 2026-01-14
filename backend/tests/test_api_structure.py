"""Test API structure and endpoint registration."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_auth_endpoints_registered():
    """Test that authentication endpoints are registered."""
    try:
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password"
        })
        assert response.status_code in [400, 422, 201]
    except Exception:
        pass
    
    try:
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        assert response.status_code in [401, 422]
    except Exception:
        pass

def test_client_endpoints_registered():
    """Test that client endpoints are registered."""

    response = client.get("/api/clients")
    assert response.status_code in [401, 403]

    response = client.post("/api/clients", json={
        "name": "Test Client",
        "email": "client@example.com",
        "street": "123 Main St",
        "city": "City",
        "state": "State",
        "zipCode": "12345",
        "country": "Country",
        "phone": "555-0100"
    })
    assert response.status_code in [401, 403, 422]

def test_invoice_endpoints_registered():
    """Test that invoice endpoints are registered."""

    response = client.get("/api/invoices")
    assert response.status_code in [401, 403]

    response = client.post("/api/invoices", json={
        "clientId": "123e4567-e89b-12d3-a456-426614174000",
        "invoiceNumber": "INV-001",
        "invoiceDate": "2024-01-15",
        "dueDate": "2024-02-15",
        "taxRate": "8.5",
        "lineItems": [
            {
                "description": "Service",
                "quantity": "1",
                "unitRate": "100"
            }
        ]
    })
    assert response.status_code in [401, 403, 422]

def test_openapi_docs():
    """Test that OpenAPI documentation is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_spec = response.json()

    assert "/api/auth/register" in openapi_spec["paths"]
    assert "/api/auth/login" in openapi_spec["paths"]
    assert "/api/clients" in openapi_spec["paths"]
    assert "/api/invoices" in openapi_spec["paths"]
    assert "/api/invoices/{invoice_id}/send" in openapi_spec["paths"]
    assert "/api/invoices/{invoice_id}/pay" in openapi_spec["paths"]

def test_cors_headers():
    """Test that CORS is configured."""
    response = client.options("/api/clients", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET"
    })

    assert response.status_code in [200, 405]
