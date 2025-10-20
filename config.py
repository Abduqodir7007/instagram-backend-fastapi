from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
