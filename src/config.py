from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+pg8000://postgres:12.34.qw.er.@45.88.137.131:5432/gps"

    class Config:
        env_file = ".env"


settings = Settings()
