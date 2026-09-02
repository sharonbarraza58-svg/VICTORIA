import os
import hashlib
import hmac
import binascii
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Importamos la conexión a BD y el modelo de usuario
from db.database import get_db  # Ajusta esto según dónde tengas tu get_db
from models.usuario import Usuario

# Cargar variables de entorno (el archivo .env)
load_dotenv()

# Configuraciones de encriptación (Extraídas de la guía del SENA)
_PBKDF2_ITERATIONS = 100_000
_SALT_BYTES = 16

# Llaves maestras: se leen del .env. Si faltan, detenemos el arranque
# de la aplicación en vez de operar con una clave insegura por defecto.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if not SECRET_KEY:
    raise RuntimeError(
        "❌ ERROR CRÍTICO DE CONFIGURACIÓN: La variable 'SECRET_KEY' no está definida en el archivo .env."
    )
if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise RuntimeError(
        "❌ ERROR CRÍTICO DE CONFIGURACIÓN: La variable 'ACCESS_TOKEN_EXPIRE_MINUTES' no está definida en el archivo .env."
    )
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)

# ==========================================
# 1. FUNCIONES DE ENCRIPTACIÓN DE CONTRASEÑA
# ==========================================
def hash_password(password: str) -> str:
    """Convierte la contraseña plana en un código indescifrable."""
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{_PBKDF2_ITERATIONS}${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña digitada con la encriptada en la base de datos."""
    try:
        iterations, salt_hex, dk_hex = hashed_password.split("$")
        salt = binascii.unhexlify(salt_hex)
        dk_stored = binascii.unhexlify(dk_hex)
        dk_new = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(dk_new, dk_stored)
    except Exception:
        return False

# ==========================================
# 2. FUNCIONES DE TOKEN JWT
# ==========================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Fabrica el pasaporte (Token JWT) guardando el número de documento del usuario."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_token_from_request(request: Request) -> str:
    """Extrae el token de la cabecera HTTP (quita la palabra 'Bearer ')."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer inválido o ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_header[7:]

# ==========================================
# 3. EL ESCUDO (INYECCIÓN DE DEPENDENCIAS)
# ==========================================
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    """Este es el guardia de seguridad. Lee el token, extrae el documento y busca al usuario."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = get_token_from_request(request)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # OJO AQUÍ: Extraemos el número de documento, no el correo
        numero_doc: str = payload.get("sub")
        if numero_doc is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Buscamos en la BD usando el número de documento
    usuario = db.query(Usuario).filter(Usuario.numero_documento == numero_doc).first()
    if usuario is None:
        raise credentials_exception
    
    return usuario

# ==========================================
# 4. EL SEGUNDO ESCUDO: Usuario activo
# ==========================================
def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Además de tener un token válido, el usuario debe estar activo.

    ANTES: el campo 'estado' existía en el modelo (para que un admin pudiera
    desactivar a alguien) pero nunca se revisaba aquí. Resultado: si
    desactivabas a un usuario, su token JWT seguía funcionando exactamente
    igual hasta que expirara solo, sin importar el cambio de estado.

    Se compara en minúsculas para no fallar por un "Activo" vs "activo".
    """
    if (current_user.estado or "").strip().lower() != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está inactiva. Contacta a un administrador.",
        )
    return current_user