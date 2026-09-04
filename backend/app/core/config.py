from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "ETF Intelligence Lab API"
    environment: str = "development"
    demo_mode: bool = True
    data_dir: Path = PROJECT_ROOT / "data" / "snapshots"
    database_path: Path = PROJECT_ROOT / "data" / "demo" / "etf_lab.duckdb"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_prefix="ETF_LAB_", env_file=".env")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
