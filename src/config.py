from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "12.34.qw.er."
    db_name: str = "gps"
    database_url: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **data):
        super().__init__(**data)
        if not self.database_url:
            self.database_url = f"postgresql+pg8000://{self.db_user}:{self.db_password}@postgres:5432/{self.db_name}"


settings = Settings()
