from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseConfig(BaseModel):
    user: str
    password: str
    name: str
    host: str
    port: int
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn(f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")


class EnvironmentConfig(BaseModel):
    environment: str
    logging_level: str


class ProviderConfig(BaseModel):
    url: str
    max_attempts: int = 5
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 10.0
    jitter_seconds: float = 0.5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file=(BASE_DIR / ".env.template", BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    run: RunConfig = RunConfig()
    db: DatabaseConfig
    env: EnvironmentConfig
    provider: ProviderConfig


settings = Settings()
