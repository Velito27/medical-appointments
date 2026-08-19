from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str | None = None

    postgres_db: str = "medical_appointments"
    postgres_user: str = "medical_user"
    postgres_password: str = "change_me"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    jwt_secret_key: str = "change-this-development-secret-key-32-plus"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    admin_email: str = "admin@example.com"
    admin_password: str = "Admin1234!"
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
