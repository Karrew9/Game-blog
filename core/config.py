from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Gameture"
    APP_DESCRIPTION: str = "A simple blog API with Clean Architecture"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./blog.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECURE_COOKIES: bool = True

    class Config:
        env_file = ".env"


settings = Settings()