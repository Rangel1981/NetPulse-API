from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    CHAT_ID: str
    DATABASE_URL: str

    # avisar o Pydantic para subir um nível e buscar o .env na raiz
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()