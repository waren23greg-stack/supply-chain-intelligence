import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Supply Chain Intelligence Engine"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    
    # LLM Settings (Defaults to OpenAI / Open-source compatible endpoints)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "demo-key-placeholder")
    MODEL_NAME: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.1
    
    # Risk Thresholds
    CRITICAL_STOCKOUT_DAYS: int = 7
    HIGH_RISK_SUPPLIER_SCORE: float = 0.70
    
    class Config:
        env_file = ".env"

settings = Settings()
