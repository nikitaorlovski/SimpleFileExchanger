from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class S3Settings(BaseModel):
    endpoint_url: str
    public_url: str
    access_key: str
    secret_key: str
    account_id: str
    bucket_name: str
    region: str = "auto"


class DBConnection(BaseModel):
    username: str
    password: str
    name: str
    host: str
    port: str


class Settings(BaseSettings):
    s3: S3Settings
    db: DBConnection
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+psycopg://{self.db.username}:{self.db.password}@{self.db.host}:{self.db.port}/{self.db.name}"


settings = Settings()
