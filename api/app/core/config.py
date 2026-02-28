from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY:           str = ""
    DATABASE_URL:         str = ""
    REDIS_URL:            str = ""
    DEBUG:                bool = False
    POSTGRES_DB:          str = ""
    POSTGRES_USER:        str = ""
    POSTGRES_PASSWORD:    str = ""
    REDIS_PASSWORD:       str = ""
    N8N_WEBHOOK_BASE_URL: str = ""

    # Vault credentials
    VAULT_URL:            str = ""
    VAULT_CLIENT_ID:      str = ""
    VAULT_CLIENT_SECRET:  str = ""

    class Config:
        env_file = ".env"

settings = Settings()