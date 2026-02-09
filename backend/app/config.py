from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Alpha Vantage API
    alpha_api_key: str

    # InfluxDB Configuration
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str
    influxdb_org: str = "finspeak"
    influxdb_bucket: str = "market_data"

    # Financial Modeling Prep API
    fmp_api_key: str

    # Ollama Configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
