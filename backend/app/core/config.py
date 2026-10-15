from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "beacon-station"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./beacon.db"
    database_echo: bool = False

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    # Keycloak / OIDC
    oidc_issuer_url: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_audience: Optional[str] = None
    oidc_jwks_url: Optional[str] = None

    # Demo mode (local only, refuses in production)
    demo_mode: bool = False

    # LLM
    llm_provider: Optional[str] = None  # openai, anthropic, gemini, ollama
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_timeout_seconds: int = 30

    # Paths
    plans_root: str = "./data/plans"
    claude_config_dir: str = os.path.expanduser("~/.claude")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def effective_demo_mode(self) -> bool:
        if self.is_production:
            return False
        return self.demo_mode


settings = Settings()