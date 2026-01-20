from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # Меняем название переменной, чтобы не путаться
    GEMINI_API_KEY: str 
    # Модель можно зашить тут жестко
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"