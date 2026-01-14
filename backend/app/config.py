"""Application configuration."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

    supabase_url: str
    supabase_key: str

    api_host: str = "0.0.0.0"
    api_port: int = 8000

settings = Settings()
