from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    base_url: str = "http://localhost:9000"
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
