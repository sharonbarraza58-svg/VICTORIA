from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.usuario import Usuario
from schemas.materiales import MaterialCreate, MaterialResponse
from services.material_service import MaterialService
from core.security import get_current_active_user

router = APIRouter()

# ANTES: este archivo llamaba a "services.obtener_materiales(db)",
# "services.crear_material(db, material)", etc., como si material_service
# fuera un módulo con funciones sueltas. Pero material_service.py define una
# CLASE (MaterialService) con métodos de instancia -> todos los endpoints
# tronaban con AttributeError. Además las rutas tenían prefijos duplicados
# ("/materiales" aquí + "/api/materiales" en main.py = /api/materiales/materiales,
# y el DELETE llegaba a duplicar hasta el prefijo completo). Se corrige
# instanciando MaterialService(db), igual que hacen ficha.py / coordinacion.py,
# y usando rutas relativas limpias.


@router.get("/", response_model=List[MaterialResponse], tags=["Materiales"])
def listar_materiales(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    service = MaterialService(db)
    return service.obtener_materiales()


@router.get("/{id_material}", response_model=MaterialResponse, tags=["Materiales"])
def obtener_material(
    id_material: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    service = MaterialService(db)
    return service.obtener_material_por_id(id_material)


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED, tags=["Materiales"])
def guardar_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    # Roles administrativos o instructores (mismo criterio que ya usaba el proyecto)
    if usuario_actual.id_rol not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para agregar material.")

    service = MaterialService(db)
    return service.crear_material(material)


@router.put(
    "/{id_material}",
    response_model=MaterialResponse,
    tags=["Materiales"],
    summary="Modificar un Material existente",
)
def modificar_material(
    id_material: int,
    material_actualizado: MaterialCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este material.")

    service = MaterialService(db)
    return service.actualizar_material(id_material, material_actualizado)


@router.delete("/{id_material}", tags=["Materiales"])
def eliminar_material_ruta(
    id_material: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar materiales.")

    service = MaterialService(db)
    return service.eliminar_material(id_material)
