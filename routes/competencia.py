from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from db.database import get_db
from models.usuario import Usuario
from models.competencia import Competencia
from schemas.competencia import CompetenciaCreate, CompetenciaResponse
from services import competencia_service as services
from core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=CompetenciaResponse, status_code=status.HTTP_201_CREATED)
def crear_competencia(
    data: CompetenciaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear competencias.")
    
    # 1. Instanciamos tu clase
    servicio = services.CompetenciaService(db)
    # 2. Llamamos al método pasando solo la data (db ya está en self)
    return servicio.crear_competencia(data)


@router.get("/", response_model=List[CompetenciaResponse])
def listar_competencias(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    servicio = services.CompetenciaService(db)
    return servicio.obtener_competencias()


@router.put("/{id_competencia}", response_model=CompetenciaResponse)
def actualizar_competencia(
    id_competencia: int,
    data: CompetenciaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar.")
    
    servicio = services.CompetenciaService(db)
    # Corregido: Llamamos al método correcto y quitamos el doble return
    return servicio.actualizar_competencia(id_competencia, data)


@router.delete("/{id_competencia}")
def eliminar_competencia(
    id_competencia: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo el admin puede eliminar.")
    

    servicio = services.CompetenciaService(db)
    # Corregido: Ahora sí llama a la función de eliminar
    try:
        return servicio.eliminar_competencia(id_competencia)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: todavía hay un programa que apunta a esta competencia.",
        )
