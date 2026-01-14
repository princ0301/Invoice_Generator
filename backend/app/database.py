"""Database connection and client."""
from supabase import create_client, Client
from app.config import settings
import sys

def get_supabase_client() -> Client:
    """Create and return a Supabase client instance."""
    try:
        client = create_client(settings.supabase_url, settings.supabase_key)
        return client
    except Exception as e:
        print(f"\n ERROR: Failed to create Supabase client")
        print(f"   {str(e)}")
        print(f"\n Check your Supabase configuration in backend/.env")
        print(f"   Current URL: {settings.supabase_url}")
        print(f"\n See backend/SETUP_REQUIRED.md for setup instructions")

        raise

supabase: Client = None

try:
    supabase = get_supabase_client()
except Exception:

    pass
