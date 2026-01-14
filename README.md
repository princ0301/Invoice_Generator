# Invoice Generator

A modern, full-stack invoice management application built with FastAPI, React, and Supabase. Create, manage, and export professional invoices with ease.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-19-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)

## ✨ Features

- 🔐 **Secure Authentication** - User registration and login with JWT tokens
- 👥 **Client Management** - Store and manage client information
- 📄 **Invoice Creation** - Build invoices with multiple line items
- 💰 **Automatic Calculations** - Subtotal, tax, and total computed automatically
- 📊 **Status Tracking** - Track invoices through draft, sent, paid, and overdue states
- 📑 **PDF Export** - Generate professional PDF invoices with ReportLab
- 🔒 **Data Security** - Row Level Security ensures users only see their own data
- ✅ **Comprehensive Testing** - 48 passing tests with property-based testing

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      React Frontend (UI)            │
│   - Invoice management              │
│   - Client management               │
│   - Authentication                  │
└─────────────────────────────────────┘
              ↓ HTTP/REST
┌─────────────────────────────────────┐
│      FastAPI Backend (API)          │
│   - REST endpoints                  │
│   - Business logic                  │
│   - PDF generation                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Supabase                       │
│   - PostgreSQL Database             │
│   - Authentication (JWT)            │
│   - Row Level Security              │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **uv** - Python package manager: `pip install uv`
- **Supabase Account** - [Sign up](https://supabase.com/)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Invoice_Generator
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials:
# SUPABASE_URL=your_supabase_project_url
# SUPABASE_KEY=your_supabase_anon_key

# Run database migration
# Go to Supabase Dashboard → SQL Editor
# Run the SQL in migrations/001_initial_schema.sql

# Start the backend server
uv run uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials:
# VITE_API_URL=http://localhost:8000
# VITE_SUPABASE_URL=your_supabase_project_url
# VITE_SUPABASE_KEY=your_supabase_anon_key

# Start the frontend server
npm run dev
```

Frontend runs at: **http://localhost:5173**

## 📁 Project Structure

```
Invoice_Generator/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API Endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── clients.py     # Client CRUD
│   │   │   ├── invoices.py    # Invoice CRUD
│   │   │   └── dependencies.py # Shared dependencies
│   │   ├── models/            # Domain Models
│   │   │   ├── client.py
│   │   │   ├── invoice.py
│   │   │   └── line_item.py
│   │   ├── services/          # Business Logic
│   │   │   └── pdf_export.py  # PDF generation
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Supabase client
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Test Suite
│   │   ├── test_models.py     # Unit tests
│   │   ├── test_properties.py # Property-based tests
│   │   ├── test_pdf_export.py # PDF tests
│   │   └── test_integration.py # Integration tests
│   ├── migrations/            # Database Schema
│   │   └── 001_initial_schema.sql
│   └── pyproject.toml         # Dependencies
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utilities
│   │   ├── pages/             # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Clients.tsx
│   │   │   ├── Invoices.tsx
│   │   │   ├── InvoiceForm.tsx
│   │   │   └── InvoiceDetail.tsx
│   │   └── types/             # TypeScript types
│   └── package.json           # Dependencies
│
├── .kiro/specs/               # Feature Specifications
│   └── invoice-generator/
│       ├── requirements.md    # Requirements
│       ├── design.md          # Design document
│       └── tasks.md           # Implementation tasks
│
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🛠️ Technology Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Supabase](https://supabase.com/)** - PostgreSQL database with authentication
- **[ReportLab](https://www.reportlab.com/)** - PDF generation
- **[Hypothesis](https://hypothesis.readthedocs.io/)** - Property-based testing
- **[Pytest](https://pytest.org/)** - Testing framework
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager

### Frontend
- **[React 19](https://react.dev/)** - UI library
- **[Vite](https://vitejs.dev/)** - Build tool
- **[Tailwind CSS](https://tailwindcss.com/)** - Styling
- **[React Router](https://reactrouter.com/)** - Navigation
- **[Axios](https://axios-http.com/)** - HTTP client
- **[Supabase JS](https://supabase.com/docs/reference/javascript/introduction)** - Authentication client

### Database
- **[PostgreSQL](https://www.postgresql.org/)** (via Supabase)
- **Row Level Security (RLS)** for data isolation
- **Automatic timestamps** and audit trails

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### API Endpoints

#### Authentication
```
POST   /api/auth/register    Register new user
POST   /api/auth/login       Login with credentials
```

#### Clients
```
GET    /api/clients          List all clients
POST   /api/clients          Create new client
GET    /api/clients/{id}     Get client by ID
PUT    /api/clients/{id}     Update client
DELETE /api/clients/{id}     Delete client
```

#### Invoices
```
GET    /api/invoices         List all invoices
POST   /api/invoices         Create new invoice
GET    /api/invoices/{id}    Get invoice by ID
PUT    /api/invoices/{id}    Update invoice
DELETE /api/invoices/{id}    Delete invoice
POST   /api/invoices/{id}/send  Mark invoice as sent
POST   /api/invoices/{id}/pay   Mark invoice as paid
GET    /api/invoices/{id}/pdf   Export invoice as PDF
```

## 🧪 Testing

### Run All Tests

```bash
cd backend
uv run pytest tests/ -v
```

### Run Specific Test Types

```bash
# Unit tests
uv run pytest tests/test_models.py -v

# Property-based tests
uv run pytest tests/test_properties.py -v

# PDF export tests
uv run pytest tests/test_pdf_export.py -v

# Integration tests
uv run pytest tests/test_integration.py -v
```

### Test Coverage

- **48 tests passing** ✅
- **11 tests skipped** (require live Supabase setup)
- **0 failures** ✅

Test types:
- **Unit Tests**: Domain models validation
- **Property-Based Tests**: 16 properties with 100+ iterations each
- **PDF Tests**: PDF generation and validation
- **Integration Tests**: End-to-end workflows

## 🔧 Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app tests/

# Format code
uv run black app/ tests/

# Lint code
uv run ruff check app/ tests/
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🗄️ Database Schema

The application uses three main tables:

### clients
- User-specific client information
- Email, address, phone details
- Protected by Row Level Security

### invoices
- Invoice metadata and status
- Links to clients
- Tracks sent/paid dates
- Protected by Row Level Security

### line_items
- Individual invoice items
- Description, quantity, unit rate
- Automatically deleted when invoice is deleted

See `backend/migrations/001_initial_schema.sql` for complete schema.

## 🔐 Security

- **JWT Authentication**: Secure token-based authentication
- **Row Level Security**: Users can only access their own data
- **Password Hashing**: Passwords are never stored in plain text
- **CORS Protection**: Configured for specific origins
- **Input Validation**: Pydantic models validate all inputs
- **SQL Injection Protection**: Parameterized queries via Supabase

## 📊 Code Statistics

- **Total Lines**: 4,397 lines
- **Backend**: 2,665 lines (Python)
- **Frontend**: 1,732 lines (TypeScript/React)
- **Database**: 120 lines (SQL)
- **Test Coverage**: 113% (test-to-code ratio)

## 🚢 Deployment

### Backend Deployment

1. **Set environment variables** on your hosting platform
2. **Run database migrations** in Supabase
3. **Deploy FastAPI app** (Heroku, Railway, Render, etc.)

```bash
# Example for production
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Deployment

1. **Build the frontend**:
   ```bash
   npm run build
   ```

2. **Deploy `dist/` folder** to:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Any static hosting service

3. **Update environment variables** with production API URL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [React](https://react.dev/)
- Database by [Supabase](https://supabase.com/)
- PDF generation by [ReportLab](https://www.reportlab.com/)
- Testing with [Hypothesis](https://hypothesis.readthedocs.io/)

## 📧 Support

For support, email support@example.com or open an issue in the repository.

## 🗺️ Roadmap

- [ ] Email invoice delivery
- [ ] Recurring invoices
- [ ] Payment tracking
- [ ] Multi-currency support
- [ ] Invoice templates
- [ ] Dashboard analytics
- [ ] Mobile app

---

**Made with ❤️ using FastAPI, React, and Supabase**
