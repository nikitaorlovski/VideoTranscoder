from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

from sqlalchemy import URL

ROOT = Path(__file__).resolve().parent.parent.parent

class DbSettings(BaseModel):
    host: str
    port: int
    name: str
    username: str
    password: str

    @property
    def url(self):
        return URL.create(drivername="postgresql+asyncpg", database=self.name, host=self.host,port=self.port,username=self.username,password=self.password)

    @property
    def sqlalchemy_url(self):
        return URL.create(drivername="postgresql+asyncpg", database=self.name, host="localhost",port=self.port,username=self.username,password=self.password)

class AuthSettings(BaseModel):
    algorithm: str = "RS256"
    private_key_path: Path = ROOT / "certs" /  "private.pem"
    public_key_path: Path = ROOT / "certs" /  "public.pem"

class Settings(BaseSettings):
    db: DbSettings
    auth: AuthSettings = AuthSettings()

    model_config = SettingsConfigDict(
        env_file= str(ROOT / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )

settings = Settings()
