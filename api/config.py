from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    db_host: str = "34.136.15.241"
    db_port: int = 5666
    db_name: str = "apg_database"
    db_user: str = "apg_adm_v1"
    db_password: str = "hfuBZyXf4Dni"
    
    # API settings
    api_title: str = "Images API"
    api_description: str = "API REST para consultar datos de imágenes por folder_name"
    api_version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 5544
    
    # Database connection pool settings
    db_min_connections: int = 10
    db_max_connections: int = 20
    
    # Cache settings
    redis_url: str = "redis://redis:6379"  # Docker service name
    cache_ttl_seconds: int = 300  # 5 minutes default
    cache_enabled: bool = True
    memory_cache_size: int = 1000  # Max items in memory cache
    
    class Config:
        env_file = ".env"

settings = Settings()
