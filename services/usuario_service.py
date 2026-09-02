from sqlalchemy.orm import Session
from models import usuario as models
from schemas import usuario as schemas
from core.security import hash_password

# NOTA: Las funciones de Rol que antes vivian aqui (obtener_roles, crear_rol,
# actualizar_rol, eliminar_rol) se eliminaron porque estaban rotas: hacian
# "from models import usuario as models" y luego usaban "models.Rol", pero el
# modulo models/usuario.py solo define la clase Usuario, no Rol. Ademas nadie
# las llamaba: la gestion de Roles real vive en services/rol_service.py
# (clase RolService), que es la que usa routes/rol.py.

# --- Servicios de Usuarios ---

def obtener_usuarios(db: Session):
    return db.query(models.Usuario).all()


def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):

    datos = usuario.model_dump()
    datos["contrasena"] = hash_password(datos.pop("contrasena"))
    db_usuario = models.Usuario(**datos)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def eliminar_usuario(db: Session, id_usuario: int):
    """Busca un usuario por su ID y lo elimina"""
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
        return True
    return False


def actualizar_usuario(db: Session, id_usuario: int, datos_actualizados: dict):
    """Busca un usuario por ID y actualiza solo los campos presentes en
    'datos_actualizados'.

    Antes recibía el objeto UsuarioUpdate completo y llamaba internamente a
    usr_act.model_dump(exclude_unset=True). Ahora recibe directamente el
    diccionario ya filtrado (ver routes/usuario.py): así la ruta puede
    quitar campos sensibles (como "estado" cuando quien edita no es
    administrador) ANTES de que lleguen aquí, sin ambigüedad sobre qué
    cuenta como "campo enviado" por el cliente.
    """
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if db_usuario:
        for key, value in datos_actualizados.items():
            setattr(db_usuario, key, value)
        db.commit()
        db.refresh(db_usuario)
    return db_usuario
