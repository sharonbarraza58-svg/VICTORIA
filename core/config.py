from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = 'VICTORIA-blog'
    PROJECT_VERSION: str = '0.0.1'
    DATABASE_URL: str
    
    # 🚀 NUEVAS VARIABLES DE SEGURIDAD REQUERIDAS:
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALLOWED_ORIGINS: str = ""

    class Config:
        env_file = '.env'
        extra = 'ignore'  # 👈 ¡ESTO ES CLAVE! Le dice a Python que ignore cualquier otra variable extra en el .env sin romperse
        

settings = Settings()