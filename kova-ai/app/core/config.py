import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    app_name: str = "Kova AI System"
    api_version: str = Field(default="v1", alias="API_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Database Configuration
    database_url: str = Field(..., alias="DATABASE_URL")
    postgres_db: str = Field(default="kova", alias="POSTGRES_DB")
    postgres_user: str = Field(default="kova", alias="POSTGRES_USER")
    postgres_password: str = Field(default="kova_pass", alias="POSTGRES_PASSWORD")
    
    # External API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    
    # Security Configuration
    secret_key: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS Configuration - convert string to list if needed
    allowed_origins: list = Field(default=["*"])
        
    def validate_required_keys(self) -> bool:
        """Validate that all required API keys are present for full functionality."""
        required_keys = {
            'openai_api_key': self.openai_api_key,
            'anthropic_api_key': self.anthropic_api_key,
            'github_token': self.github_token,
            'pinecone_api_key': self.pinecone_api_key
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        
        if missing_keys:
            print(f"⚠️  Warning: Missing API keys: {', '.join(missing_keys)}")
            print("   Some functionality may be limited. Please configure these keys in .env file.")
            return False
        return True


# Create global settings instance
settings = Settings()