from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 1. Importamos la configuración que ya hiciste con Pydantic
from core.config import settings

# 2. Obtenemos la URL directamente de los settings (que lee el .env automáticamente)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 3. Crear el engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Configurar el generador de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base para los modelos
Base = declarative_base()

def get_db():
    """Provee una sesion de base de datos y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()