# Invoice Generator Frontend

A React-based frontend for the Invoice Generator application.

## Features

- User authentication (login/register)
- Client management (create, edit, delete clients)
- Invoice management (create, edit, delete invoices)
- Invoice status tracking (draft, sent, paid, overdue)
- PDF export functionality
- Responsive design with Tailwind CSS

## Tech Stack

- React 19
- TypeScript
- React Router for navigation
- Tailwind CSS for styling
- Axios for API calls
- Supabase for authentication
- Vite for build tooling

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on http://localhost:8000
- Supabase project configured

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
Create a `.env` file with:
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_KEY=your_supabase_anon_key
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Application Structure

- `/src/pages` - Page components (Login, Register, Invoices, Clients, etc.)
- `/src/components` - Reusable components (Layout, ProtectedRoute)
- `/src/contexts` - React contexts (AuthContext)
- `/src/lib` - Utility libraries (API client, Supabase client)
- `/src/types` - TypeScript type definitions

## Usage

1. Register a new account or login
2. Create clients in the Clients page
3. Create invoices in the Invoices page
4. Track invoice status and download PDFs
5. Mark invoices as sent or paid

## API Integration

The frontend communicates with the FastAPI backend through REST endpoints:
- Authentication: `/api/auth/*`
- Invoices: `/api/invoices/*`
- Clients: `/api/clients/*`

All requests include JWT authentication tokens in the Authorization header.
