from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # N8N
    N8N_WEBHOOK_BASE_URL: str = ""

    class Config:
        env_file = ".env"

settings = Settings()