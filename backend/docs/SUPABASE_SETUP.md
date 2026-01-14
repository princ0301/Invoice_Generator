# Supabase Setup Guide

This guide walks you through setting up Supabase for the Invoice Generator application.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- Python 3.11+ installed
- Backend dependencies installed (`cd backend && uv sync`)

## Step 1: Create a Supabase Project

1. Go to https://supabase.com and sign in
2. Click **New Project**
3. Fill in the project details:
   - **Name**: Invoice Generator (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region to your users
4. Click **Create new project**
5. Wait for the project to be provisioned (takes ~2 minutes)

## Step 2: Get Your API Credentials

1. Once your project is ready, go to **Settings** > **API**
2. Copy the following values:
   - **Project URL**: This is your `SUPABASE_URL`
   - **anon public key**: This is your `SUPABASE_KEY`

3. Update your `backend/.env` file:

```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-public-key
```

## Step 3: Apply Database Migration

### Using Supabase Dashboard (Recommended)

1. In your Supabase project, go to **SQL Editor**
2. Click **New Query**
3. Open `backend/migrations/001_initial_schema.sql`
4. Copy the entire contents
5. Paste into the SQL editor
6. Click **Run** (or press Ctrl+Enter)
7. You should see "Success. No rows returned"

### Verify Tables Created

1. Go to **Table Editor** in the left sidebar
2. You should see three tables:
   - `clients`
   - `invoices`
   - `line_items`

## Step 4: Configure Authentication

### Enable Email Authentication

1. Go to **Authentication** > **Providers**
2. Ensure **Email** is enabled (it should be by default)
3. Configure email settings:
   - **Enable email confirmations**: Toggle based on your needs
   - For development, you can disable confirmations
   - For production, enable confirmations

### Configure Site URL and Redirect URLs

1. Go to **Authentication** > **URL Configuration**
2. Set the following:
   - **Site URL**: 
     - Development: `http://localhost:5173`
     - Production: Your production frontend URL
   - **Redirect URLs**: Add both:
     - `http://localhost:5173/**`
     - Your production URL (if applicable)

### Configure Email Templates (Optional)

1. Go to **Authentication** > **Email Templates**
2. Customize the following templates:
   - **Confirm signup**: Sent when users register
   - **Magic Link**: For passwordless login (if using)
   - **Change Email Address**: When users change email
   - **Reset Password**: For password recovery

## Step 5: Verify Database Setup

Run the verification script:

```bash
cd backend
python scripts/verify_database.py
```

Expected output:
```
============================================================
Invoice Generator - Database Verification
============================================================

🔍 Verifying Supabase connection...
   URL: https://your-project-ref.supabase.co
✅ Connection successful!

🔍 Verifying database tables...
✅ Table 'clients' exists
✅ Table 'invoices' exists
✅ Table 'line_items' exists

🔍 Verifying Row Level Security...
✅ RLS is enabled (unauthenticated access returns empty)

============================================================
VERIFICATION SUMMARY
============================================================
✅ PASS - Connection
✅ PASS - Tables
✅ PASS - Row Level Security
✅ PASS - Constraints
============================================================

🎉 All checks passed! Database is configured correctly.
```

## Step 6: Test Authentication

You can test authentication using the Supabase dashboard or Python:

### Using Supabase Dashboard

1. Go to **Authentication** > **Users**
2. Click **Add user** > **Create new user**
3. Enter an email and password
4. Click **Create user**
5. The user will appear in the users list

### Using Python

Create a test script or use Python REPL:

```python
from supabase import create_client

# Your credentials
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-anon-public-key"

# Create client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Register a new user
response = supabase.auth.sign_up({
    "email": "test@example.com",
    "password": "SecurePassword123!"
})
print("User created:", response.user.id)

# Login
response = supabase.auth.sign_in_with_password({
    "email": "test@example.com",
    "password": "SecurePassword123!"
})
print("Login successful:", response.user.email)
print("Access token:", response.session.access_token)
```

## Step 7: Understanding Row Level Security (RLS)

The database schema includes Row Level Security policies that ensure:

1. **Data Isolation**: Users can only access their own data
2. **Automatic Filtering**: Queries automatically filter by `user_id`
3. **Security by Default**: No additional code needed in the application

### How RLS Works

When a user is authenticated:
- Their user ID is available as `auth.uid()`
- All queries automatically filter by `user_id = auth.uid()`
- Users cannot see or modify other users' data

Example:
```python
# User A is authenticated
supabase.table('clients').select('*').execute()
# Returns only clients where user_id = User A's ID

# User B is authenticated
supabase.table('clients').select('*').execute()
# Returns only clients where user_id = User B's ID
```

### Testing RLS

1. Create two test users in the dashboard
2. Use each user's credentials to authenticate
3. Create clients/invoices with each user
4. Verify each user can only see their own data

## Troubleshooting

### Connection Issues

**Error**: "Invalid API key"
- **Solution**: Double-check your `SUPABASE_KEY` in `.env`
- Make sure you're using the **anon public** key, not the service role key

**Error**: "Failed to connect"
- **Solution**: Check your `SUPABASE_URL` is correct
- Ensure your internet connection is working
- Verify your Supabase project is active

### Migration Issues

**Error**: "relation already exists"
- **Solution**: Tables already exist. You can either:
  - Skip the migration (tables are already set up)
  - Drop existing tables and re-run (⚠️ destroys data)

**Error**: "permission denied"
- **Solution**: Make sure you're running the SQL in the Supabase dashboard
- The anon key doesn't have permission to create tables

### Authentication Issues

**Error**: "Email not confirmed"
- **Solution**: 
  - Check **Authentication** > **Settings**
  - Disable "Enable email confirmations" for development
  - Or confirm the email via the link sent

**Error**: "Invalid login credentials"
- **Solution**: 
  - Verify the email and password are correct
  - Check if the user exists in **Authentication** > **Users**

## Security Best Practices

1. **Never commit `.env` files**: Keep credentials secret
2. **Use service role key carefully**: Only use in backend, never in frontend
3. **Enable email confirmation in production**: Verify user emails
4. **Use strong passwords**: Enforce password requirements
5. **Monitor authentication logs**: Check for suspicious activity
6. **Rotate keys periodically**: Update API keys regularly

## Next Steps

After completing this setup:

1. ✅ Database schema is configured
2. ✅ Authentication is enabled
3. ✅ Row Level Security is active
4. ➡️ Proceed to Task 3: Implement backend domain models
5. ➡️ Then Task 4: Implement backend API with FastAPI

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Authentication Guide](https://supabase.com/docs/guides/auth)
