from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.coordinacion import Coordinacion
from models.usuario import Usuario
from schemas.coordinacion import CoordinacionCreate, CoordinacionResponse
from services.coordinacion_service import CoordinacionService
from core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=CoordinacionResponse, status_code=status.HTTP_201_CREATED)
def crear_coordinacion(
    data: CoordinacionCreate, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    # Solo rol 1 (Admin) puede crear coordinaciones
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear coordinaciones.")
        
    service = CoordinacionService(db)
    return service.crear_coordinacion(data)


@router.get("/", response_model=List[CoordinacionResponse])
def listar_coordinaciones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    # Cualquier usuario logueado puede verlas
    service = CoordinacionService(db)
    return service.obtener_coordinaciones()


@router.get("/{id_coordinacion}", response_model=CoordinacionResponse)
def obtener_coordinacion(
    id_coordinacion: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    service = CoordinacionService(db)
    return service.obtener_coordinacion_por_id(id_coordinacion)


@router.put("/{id_coordinacion}", response_model=CoordinacionResponse)
def actualizar_coordinacion(
    id_coordinacion: int,
    data: CoordinacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar coordinaciones.")
        
    service = CoordinacionService(db)
    return service.actualizar_coordinacion(id_coordinacion, data)


@router.delete("/{id_coordinacion}", status_code=status.HTTP_200_OK)
def eliminar_coordinacion(
    id_coordinacion: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar coordinaciones.")
        
    service = CoordinacionService(db)
    return service.eliminar_coordinacion(id_coordinacion)