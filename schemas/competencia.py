from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

from core.validators import anti_scripting

class CompetenciaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_carga: datetime

class CompetenciaCreate(CompetenciaBase):
    # ESCUDO ANTI-XSS. "descripcion" es Optional, anti_scripting ya maneja None.
    @field_validator("nombre", "descripcion")
    @classmethod
    def _bloquear_scripting(cls, valor):
        return anti_scripting(valor)

class CompetenciaResponse(CompetenciaBase):
    id_competencia: int

    class Config:
        from_attributes = True