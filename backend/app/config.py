from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://snakelog:snakelog@localhost:5432/snakelog"
    secret_key: str = "zmien-mnie-na-demo"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    frontend_url: str = "http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()