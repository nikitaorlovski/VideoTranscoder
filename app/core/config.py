from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class DbSettings(BaseSettings):
    host: str
    port: int
    db_name: str
    username: str
    password: str

    @property
    def url(self):
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class Settings(BaseSettings):
    db: DbSettings = DbSettings()

    SettingsConfigDict(
        env_file= ROOT / ".env",
        env_nested_delimiter="__"
    )

settings = Settings()
