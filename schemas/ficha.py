from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

from core.validators import anti_scripting

class FichaBase(BaseModel):
    estado: str
    fecha_inicio: datetime
    fecha_fin: datetime
    id_programa: Optional[int] = None

class FichaCreate(FichaBase):
    # ESCUDO ANTI-XSS: "estado" es el único campo de texto libre aquí.
    @field_validator("estado")
    @classmethod
    def _bloquear_scripting(cls, valor):
        return anti_scripting(valor)

class FichaResponse(FichaBase):
    id_ficha: int

    class Config:
        from_attributes = True