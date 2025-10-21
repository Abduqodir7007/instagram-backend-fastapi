from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OTP_CODE_EXPIRATION_TIME: int
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
