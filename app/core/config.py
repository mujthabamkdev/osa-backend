from typing import List, Optional, Union

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "OSA Backend"
    DEBUG: bool = True
    CORS_ORIGINS: Optional[Union[str, List[str]]] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
