from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    secret_key: str = Field(default="your-secret-key-change-in-production", description="应用密钥")

    github_client_id: str = Field(default="", description="GitHub OAuth App Client ID")
    github_client_secret: str = Field(default="", description="GitHub OAuth App Client Secret")

    google_client_id: str = Field(default="", description="Google OAuth Client ID")
    google_client_secret: str = Field(default="", description="Google OAuth Client Secret")

    class Config:
        env_file = ".env"


settings = Settings()

