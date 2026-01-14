# Invoice Generator Backend

FastAPI backend for the Invoice Generator application with Supabase integration.

## Features

- 🔐 User authentication with Supabase Auth
- 👥 Client management (CRUD operations)
- 📄 Invoice management with line items
- 💰 Automatic calculations (subtotal, tax, total)
- 📊 Invoice status tracking (draft, sent, paid, overdue)
- 📑 PDF export with ReportLab
- 🔒 Row Level Security (RLS) for data isolation
- ✅ Comprehensive test coverage

## Setup

### Prerequisites
- Python 3.11+
- uv (Python package manager)
- Supabase account and project

### Installation

1. Install dependencies using uv:
```bash
uv sync
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
```

3. Set up the database:
   - Go to your Supabase project
   - Run the SQL migration in `migrations/001_initial_schema.sql`
   - This creates tables and RLS policies

4. Run the development server:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Testing

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test Types
```bash
# Unit tests only
uv run pytest tests/test_models.py -v

# Property-based tests only
uv run pytest tests/test_properties.py -v

# PDF export tests
uv run pytest tests/test_pdf_export.py -v

# API structure tests
uv run pytest tests/test_api_structure.py -v

# Integration tests (requires Supabase setup)
uv run pytest tests/test_integration.py -v
```

### Test Coverage
- **Unit Tests**: Domain models (Client, Invoice, LineItem)
- **Property-Based Tests**: 16 properties with 100+ iterations each
- **PDF Export Tests**: PDF generation and validation
- **API Structure Tests**: Endpoint registration and configuration
- **Integration Tests**: End-to-end workflows

See `INTEGRATION_TEST_SUMMARY.md` for detailed test documentation.

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── clients.py    # Client management
│   │   └── invoices.py   # Invoice management
│   ├── models/           # Domain models
│   │   ├── client.py
│   │   ├── invoice.py
│   │   └── line_item.py
│   ├── services/         # Business logic
│   │   └── pdf_export.py
│   ├── config.py         # Configuration
│   ├── database.py       # Database connection
│   └── main.py           # FastAPI application
├── tests/                # Test suite
│   ├── test_models.py
│   ├── test_properties.py
│   ├── test_pdf_export.py
│   ├── test_api_structure.py
│   └── test_integration.py
├── migrations/           # Database migrations
│   ├── 001_initial_schema.sql
│   └── README.md
└── pyproject.toml        # Dependencies
