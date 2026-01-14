-- Invoice Generator Database Schema
-- This migration creates the core tables for the invoice generator system
-- with Row Level Security policies to ensure users can only access their own data

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CLIENTS TABLE
-- ============================================================================
-- Stores client information for invoicing
CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  street TEXT,
  city TEXT,
  state TEXT,
  zip_code TEXT,
  country TEXT,
  phone TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster user-based queries
CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id);

-- Enable Row Level Security
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own clients
CREATE POLICY "Users can only access their own clients"
  ON clients FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- INVOICES TABLE
-- ============================================================================
-- Stores invoice header information
CREATE TABLE IF NOT EXISTS invoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
  invoice_number TEXT UNIQUE NOT NULL,
  invoice_date DATE NOT NULL,
  due_date DATE NOT NULL,
  tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
  status TEXT NOT NULL CHECK (status IN ('draft', 'sent', 'paid', 'overdue')),
  sent_date TIMESTAMP WITH TIME ZONE,
  paid_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraint: due_date must be on or after invoice_date
  CONSTRAINT valid_date_range CHECK (due_date >= invoice_date)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);

-- Enable Row Level Security
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own invoices
CREATE POLICY "Users can only access their own invoices"
  ON invoices FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- LINE ITEMS TABLE
-- ============================================================================
-- Stores individual line items for each invoice
CREATE TABLE IF NOT EXISTS line_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  quantity DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
  unit_rate DECIMAL(10,2) NOT NULL CHECK (unit_rate > 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster invoice-based queries
CREATE INDEX IF NOT EXISTS idx_line_items_invoice_id ON line_items(invoice_id);

-- Enable Row Level Security
ALTER TABLE line_items ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can access line items of their invoices
CREATE POLICY "Users can access line items of their invoices"
  ON line_items FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM invoices
      WHERE invoices.id = line_items.invoice_id
      AND invoices.user_id = auth.uid()
    )
  );

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================
-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for clients table
CREATE TRIGGER update_clients_updated_at
  BEFORE UPDATE ON clients
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for invoices table
CREATE TRIGGER update_invoices_updated_at
  BEFORE UPDATE ON invoices
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE clients IS 'Stores client information for invoicing';
COMMENT ON TABLE invoices IS 'Stores invoice header information with status tracking';
COMMENT ON TABLE line_items IS 'Stores individual line items for each invoice';

COMMENT ON COLUMN invoices.status IS 'Invoice status: draft, sent, paid, or overdue';
COMMENT ON COLUMN invoices.tax_rate IS 'Tax rate as a percentage (e.g., 8.5 for 8.5%)';
COMMENT ON COLUMN line_items.quantity IS 'Quantity of items (must be positive)';
COMMENT ON COLUMN line_items.unit_rate IS 'Price per unit (must be positive)';
