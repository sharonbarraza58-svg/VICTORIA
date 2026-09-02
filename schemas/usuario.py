from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
from typing import Optional

from core.validators import anti_scripting


class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    id_rol: int
    estado: Optional[str] = "activo"
    fecha_nacimiento: date
    numero_documento: str = Field(..., max_length=20)
    tipo_documento: str = Field(..., max_length=20)
    telefono: Optional[str] = Field(None, max_length=20)
    correo_personal: EmailStr = Field(..., max_length=100)
    correo_sena: EmailStr = Field(..., max_length=100)
    
    # Todos estos ID son opcionales para permitir la creación de Administradores o Instructores
    id_ficha: Optional[int] = None
    id_coordinacion: Optional[int] = None

# 2. Esquema de Creación (Seguridad: EXIGE la contraseña para registrarse)
class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=6)

    # ESCUDO ANTI-XSS: se aplica a los campos de texto libre heredados de
    # UsuarioBase. A propósito NO incluye "contrasena": la clave se hashea
    # de inmediato con PBKDF2 y nunca se renderiza como HTML, así que
    # restringir sus caracteres solo reduciría su entropía sin aportar
    # seguridad real. Tampoco incluye correo_personal/correo_sena porque
    # EmailStr ya obliga un formato de correo válido (no cabe HTML/JS ahí).
    @field_validator(
        "nombre", "apellido", "estado",
        "numero_documento", "tipo_documento", "telefono",
    )
    @classmethod
    def _bloquear_scripting(cls, valor):
        return anti_scripting(valor)


# 2-bis. Esquema para el registro PÚBLICO (POST /api/v1/auth/register).
#
# A propósito NO hereda de UsuarioBase/UsuarioCreate: esos dos tienen
# "id_rol: int" como campo obligatorio que el cliente controla libremente.
# Usar esos schemas en una ruta pública (sin autenticación) le permite a
# CUALQUIER persona autoasignarse "id_rol": 1 (administrador) al
# registrarse, sin que ningún chequeo de permisos en el resto de la API
# (routes/proyecto.py, routes/rol.py, etc.) pueda hacer nada al respecto
# -- el usuario YA entra siendo "administrador" desde el registro.
#
# Este schema deliberadamente no tiene "id_rol" ni "estado": ambos los
# asigna el servidor (ver AuthService.registrar_usuario), nunca el cliente.
class UsuarioRegistroPublico(BaseModel):
    nombre: str = Field(..., max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    fecha_nacimiento: date
    numero_documento: str = Field(..., max_length=20)
    tipo_documento: str = Field(..., max_length=20)
    telefono: Optional[str] = Field(None, max_length=20)
    correo_personal: EmailStr = Field(..., max_length=100)
    correo_sena: EmailStr = Field(..., max_length=100)
    id_ficha: Optional[int] = None
    id_coordinacion: Optional[int] = None
    contrasena: str = Field(..., min_length=6)

    # ESCUDO ANTI-XSS: este schema es la puerta pública del registro, así
    # que necesita el mismo blindaje que UsuarioCreate.
    @field_validator("nombre", "apellido", "numero_documento", "tipo_documento", "telefono")
    @classmethod
    def _bloquear_scripting(cls, valor):
        return anti_scripting(valor)

# 3. Esquema de Actualización (PUT). Todos los campos son opcionales:
#    solo se actualiza lo que el cliente realmente envíe. A propósito NO
#    incluye "contrasena": cambiar la clave debería ser un endpoint aparte.
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    # "estado" se queda como campo del schema (lo necesita el admin para
    # activar/desactivar a otros), pero la ruta (routes/usuario.py) ahora
    # ignora este valor cuando quien edita NO es administrador. Antes, un
    # usuario normal editando su propio perfil (algo que sí tiene permitido)
    # podía mandar "estado": "activo" y reactivarse a sí mismo aunque un
    # admin lo hubiera desactivado.
    estado: Optional[str] = None
    telefono: Optional[str] = None
    correo_personal: Optional[EmailStr] = None
    id_ficha: Optional[int] = None
    id_coordinacion: Optional[int] = None

    # ESCUDO ANTI-XSS: mismos campos de texto libre que en Create, ahora
    # todos Optional porque en un PUT el cliente solo manda lo que cambia.
    @field_validator("nombre", "apellido", "estado", "telefono")
    @classmethod
    def _bloquear_scripting(cls, valor):
        return anti_scripting(valor)

# 4. Esquema de Respuesta (Seguridad: NUNCA devuelve la contraseña, pero SÍ el ID autoincrementado)
class UsuarioResponse(UsuarioBase):
    id_usuario: int
    fecha_creacion: datetime
    rol_nombre: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    numero_documento: Optional[str] = None