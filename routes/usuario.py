from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from db.database import get_db
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from services import usuario_service as services
from core.security import get_current_active_user

router = APIRouter()



@router.get("/", response_model=List[UsuarioResponse], tags=["Usuarios"])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    return services.obtener_usuarios(db)


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def guardar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear usuarios.")
    try:
        return services.crear_usuario(db, usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Error de Integridad: el número de documento o alguno de los correos ya existe, o alguna de las llaves foráneas no es válida.",
        )


@router.put("/{id_usuario}", response_model=UsuarioResponse, tags=["Usuarios"])
def modificar_usuario(
    id_usuario: int,
    usuario_actualizado: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    # Un usuario puede editar su propia información; solo el admin puede editar a otros.
    if usuario_actual.id_rol != 1 and usuario_actual.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este usuario.")


    datos_actualizados = usuario_actualizado.model_dump(exclude_unset=True)
    if usuario_actual.id_rol != 1:
        datos_actualizados.pop("estado", None)

    db_usuario = services.actualizar_usuario(db, id_usuario, datos_actualizados)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="No se encontró el Usuario que deseas modificar")
    return db_usuario


@router.delete("/{id_usuario}", tags=["Usuarios"])
def borrar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_active_user),
):
    if usuario_actual.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar usuarios.")

    exito = services.eliminar_usuario(db, id_usuario)
    if not exito:
        raise HTTPException(status_code=404, detail="No se encontró el Usuario que deseas eliminar")
    return {"message": f"Usuario con ID {id_usuario} eliminado correctamente"}
