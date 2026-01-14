"""Test basic setup and configuration."""
import pytest
from app.config import settings
from app.database import supabase
from app.main import app

def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.supabase_url is not None
    assert settings.supabase_key is not None
    assert settings.api_host is not None
    assert settings.api_port is not None

def test_supabase_client_created():
    """Test that Supabase client is created."""
    assert supabase is not None

def test_fastapi_app_created():
    """Test that FastAPI app is created."""
    assert app is not None
    assert app.title == "Invoice Generator API"
