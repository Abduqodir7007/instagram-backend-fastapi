from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OTP_CODE_EXPIRATION_TIME: int
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PORT: int | None = None
    MAIL_SERVER: str | None = None

    JWT_ALGORITHM: str
    JWT_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()
