from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.usuario import Usuario
from models.rol import Rol
from models.ficha import Ficha
from models.programa import Programa
from models.competencia import Competencia
from models.materiales import Material
from core.security import get_current_active_user

router = APIRouter()


def require_instructor(usuario: Usuario):
    if not usuario.rol or usuario.rol.nombre_rol.lower() != "instructor":
        raise HTTPException(status_code=403, detail="Esta sección es exclusiva para instructores.")
    return usuario


@router.get("/me")
def instructor_me(usuario: Usuario = Depends(get_current_active_user)):
    require_instructor(usuario)
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "nombre_completo": f"{usuario.nombre} {usuario.apellido or ''}".strip(),
        "numero_documento": usuario.numero_documento,
        "correo_sena": usuario.correo_sena,
        "estado": usuario.estado,
        "rol": usuario.rol.nombre_rol,
    }


@router.get("/{id_usuario}/fichas")
def fichas_instructor(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    if id_usuario != usuario.id_usuario:
        raise HTTPException(status_code=403, detail="Solo puedes consultar tus propias fichas.")

    fichas = db.query(Ficha).filter(Ficha.id_usuario == usuario.id_usuario).all()
    resultado = []
    for ficha in fichas:
        programa = db.query(Programa).filter(Programa.id_programa == ficha.id_programa).first() if ficha.id_programa else None
        total = db.query(Usuario).join(Rol, Usuario.id_rol == Rol.id_rol).filter(
            Usuario.id_ficha == ficha.id_ficha,
            Rol.nombre_rol.ilike("aprendiz")
        ).count()
        resultado.append({
            "id_ficha": ficha.id_ficha,
            "programa": programa.nombre if programa else "Sin programa asignado",
            "id_programa": ficha.id_programa,
            "estado": ficha.estado,
            "fecha_inicio": ficha.fecha_inicio,
            "fecha_fin": ficha.fecha_fin,
            "total_aprendices": total,
        })
    return resultado


@router.get("/fichas/{id_ficha}/aprendices")
def aprendices_ficha(
    id_ficha: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    ficha = db.query(Ficha).filter(Ficha.id_ficha == id_ficha, Ficha.id_usuario == usuario.id_usuario).first()
    if not ficha:
        raise HTTPException(status_code=404, detail="La ficha no está asignada a este instructor.")

    aprendices = db.query(Usuario).join(Rol, Usuario.id_rol == Rol.id_rol).filter(
        Usuario.id_ficha == id_ficha,
        Rol.nombre_rol.ilike("aprendiz")
    ).all()
    return [
        {
            "id_usuario": a.id_usuario,
            "nombre_apellido": f"{a.nombre} {a.apellido or ''}".strip(),
            "documento": a.numero_documento,
            "correo_sena": a.correo_sena,
            "estado": a.estado,
        }
        for a in aprendices
    ]


@router.get("/fichas/{id_ficha}/competencias")
def competencias_ficha(
    id_ficha: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    ficha = db.query(Ficha).filter(Ficha.id_ficha == id_ficha, Ficha.id_usuario == usuario.id_usuario).first()
    if not ficha:
        raise HTTPException(status_code=404, detail="La ficha no está asignada a este instructor.")
    if not ficha.id_programa:
        return []
    return db.query(Competencia).filter(Competencia.id_programa == ficha.id_programa).all()


@router.get("/{id_usuario}/materiales")
def materiales_instructor(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    if id_usuario != usuario.id_usuario:
        raise HTTPException(status_code=403, detail="Solo puedes consultar tus materiales.")
    materiales = db.query(Material).filter(
        (Material.id_usuario == usuario.id_usuario) | (Material.id_usuario.is_(None))
    ).all()
    return materiales


@router.get("/{id_usuario}/resumen")
def resumen_instructor(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    if id_usuario != usuario.id_usuario:
        raise HTTPException(status_code=403, detail="Solo puedes consultar tu resumen.")
    fichas = db.query(Ficha).filter(Ficha.id_usuario == usuario.id_usuario).all()
    aprendices = db.query(Usuario).join(Rol, Usuario.id_rol == Rol.id_rol).join(
        Ficha, Usuario.id_ficha == Ficha.id_ficha
    ).filter(Ficha.id_usuario == usuario.id_usuario, Rol.nombre_rol.ilike("aprendiz")).count()
    return {
        "fichas": len(fichas),
        "aprendices": aprendices,
        "materiales": db.query(Material).filter(
            (Material.id_usuario == usuario.id_usuario) | (Material.id_usuario.is_(None))
        ).count(),
    }


@router.get("/{id_usuario}/notificaciones")
def notificaciones_instructor(
    id_usuario: int,
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    if id_usuario != usuario.id_usuario:
        raise HTTPException(status_code=403, detail="Solo puedes consultar tus notificaciones.")
    # El modelo actual del proyecto todavía no tiene tabla Notificacion.
    # Se deja el endpoint listo para que el frontend no se rompa y se pueda
    # agregar la tabla en una siguiente migración.
    return []


@router.get("/fichas/{id_ficha}/entregables")
def entregables_ficha(
    id_ficha: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    ficha = db.query(Ficha).filter(Ficha.id_ficha == id_ficha, Ficha.id_usuario == usuario.id_usuario).first()
    if not ficha:
        raise HTTPException(status_code=404, detail="La ficha no está asignada a este instructor.")
    # El modelo entregable todavía no está presente en esta versión del proyecto.
    return []


@router.get("/entregables/{id_entregable}/evidencias")
def evidencias_entregable(
    id_entregable: int,
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    # Se activará cuando se agreguen las tablas Entregable/Evidencia.
    return []


@router.get("/entregables/{id_entregable}")
def entregable(
    id_entregable: int,
    usuario: Usuario = Depends(get_current_active_user),
):
    require_instructor(usuario)
    raise HTTPException(status_code=404, detail="El módulo de entregables todavía no está creado en la base de datos actual.")
