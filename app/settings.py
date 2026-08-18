from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):

    DATABASE_URL : str
    ALGORITHM : str
    SECRET_KEY : str

    # NEW: added with a safe default so existing .env files (which only had
    # DATABASE_URL / ALGORITHM / SECRET_KEY) keep working without edits.
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30

    model_config = SettingsConfigDict(
        env_file = ".env",
        extra = "ignore"
    )


settings = Settings()
