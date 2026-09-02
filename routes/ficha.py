from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from db.database import get_db
from models.usuario import Usuario


from schemas.ficha import FichaCreate, FichaResponse
from services.ficha_service import FichaService
from core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=FichaResponse, status_code=status.HTTP_201_CREATED)
def crear_ficha(
    data: FichaCreate, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    # Validamos que solo los roles con permisos (ej. 1 y 2) puedan crear
    if usuario_actual.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear fichas.")
        
    service = FichaService(db)
    try:
        return service.crear_ficha(data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El id_programa indicado no existe.")


@router.get("/", response_model=List[FichaResponse])
def listar_fichas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    service = FichaService(db)
    return service.obtener_fichas()


@router.get("/{id_ficha}", response_model=FichaResponse)
def obtener_ficha(
    id_ficha: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    service = FichaService(db)
    return service.obtener_ficha_por_id(id_ficha)


@router.put("/{id_ficha}", response_model=FichaResponse)
def actualizar_ficha(
    id_ficha: int,
    data: FichaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar fichas.")
        
    service = FichaService(db)
    return service.actualizar_ficha(id_ficha, data)


@router.delete("/{id_ficha}", status_code=status.HTTP_200_OK)
def eliminar_ficha(
    id_ficha: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    # Una acción tan delicada como borrar una ficha podría estar restringida solo al rol 1
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador principal puede eliminar fichas.")
    

    service = FichaService(db)
    try:
        return service.eliminar_ficha(id_ficha)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: todavía hay un programa que apunta a esta ficha.",
        )
