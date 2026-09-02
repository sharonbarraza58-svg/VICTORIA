from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.usuario import Usuario
from schemas.rol import RolCreate, RolResponse
from services.rol_service import RolService
from core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
def crear_rol(data: RolCreate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_active_user)):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear roles.")
    servicio = RolService(db)
    return servicio.crear_rol(data)

@router.get("/", response_model=List[RolResponse])
def listar_roles(db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_active_user)):
    servicio = RolService(db)
    return servicio.obtener_roles()

@router.put("/{id_rol}", response_model=RolResponse)
def actualizar_rol(
    id_rol: int, 
    data: RolCreate, 
    db: Session = Depends(get_db), 
    usuario_actual: Usuario = Depends(get_current_active_user)
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar roles.")
    servicio = RolService(db)
    return servicio.actualizar_rol(id_rol, data)

@router.delete("/{id_rol}")
def eliminar_rol(id_rol: int, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_active_user)):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar roles.")
    servicio = RolService(db)
    return servicio.eliminar_rol(id_rol)