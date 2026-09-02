from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.usuario import Usuario
from schemas.proyecto import ProyectoCreate, ProyectoResponse
from services.proyecto_service import ProyectoService
from core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=ProyectoResponse, status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    data: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear proyectos.")

    service = ProyectoService(db)
    return service.crear_proyecto(data)


@router.get("/", response_model=List[ProyectoResponse])
def listar_proyectos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    service = ProyectoService(db)
    return service.obtener_proyectos()


@router.get("/{id_proyecto}", response_model=ProyectoResponse)
def obtener_proyecto(
    id_proyecto: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    service = ProyectoService(db)
    return service.obtener_proyecto_por_id(id_proyecto)


@router.put("/{id_proyecto}", response_model=ProyectoResponse)
def actualizar_proyecto(
    id_proyecto: int,
    data: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar proyectos.")

    service = ProyectoService(db)
    return service.actualizar_proyecto(id_proyecto, data)


@router.delete("/{id_proyecto}", status_code=status.HTTP_200_OK)
def eliminar_proyecto(
    id_proyecto: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar proyectos.")

    service = ProyectoService(db)
    return service.eliminar_proyecto(id_proyecto)
