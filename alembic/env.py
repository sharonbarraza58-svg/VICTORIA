import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

# 2. Configurar el logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Importar Base y modelos para autogenerate

# IMPORTANTE: Asegúrate de importar tus modelos aquí para que sean detectados
# Ejemplo correcto:
from db.database import Base

# 🚀 IMPORTACIONES CORREGIDAS (Cada modelo desde su propio archivo):
from models.usuario import Usuario
from models.rol import Rol
from models.programa import Programa
from models.ficha import Ficha
from models.competencia import Competencia
from models.coordinacion import Coordinacion
from models.proyecto import Proyecto
from models.materiales import Material

target_metadata = Base.metadata

# 4. Configurar la URL de la base de datos
# Usamos una cadena vacía como fallback si la variable no existe
db_url = os.environ.get('DATABASE_URL', '')
config.set_main_option('sqlalchemy.url', db_url)