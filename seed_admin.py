"""
Script de arranque -- correr UNA SOLA VEZ, a mano, para crear los roles
base y el primer administrador.

Por qué existe: la API pública (POST /api/v1/auth/register) nunca deja
que un cliente se autoasigne el rol "administrador" (ver
schemas/usuario.py -> UsuarioRegistroPublico y services/auth_service.py).
Eso es correcto y necesario, pero significa que la primera cuenta
administradora no puede salir de ahí -- y POST /api/usuarios (que sí
puede crear administradores) exige estar logueado COMO administrador.
Este script rompe ese círculo insertando directo en la base de datos,
por fuera de la API.

Uso:
    cd victoria
    python seed_admin.py

Después de correrlo UNA vez, bórralo o muévelo fuera del deploy: no debe
quedar expuesto ni volver a ejecutarse en producción (si lo corres dos
veces, simplemente no hace nada porque detecta que el admin ya existe).
"""
import getpass
from datetime import datetime
from db.database import SessionLocal
from models.rol import Rol
from models.usuario import Usuario
from core.security import hash_password

# Los 4 roles base del dominio (mismos nombres que el script SQL original
# usaba en su CHECK constraint, antes de moverlos a una tabla aparte).
ROLES_BASE = ["administrador", "instructor", "coordinador", "aprendiz"]


def obtener_o_crear_roles(db):
    roles = {}
    for nombre in ROLES_BASE:
        rol = db.query(Rol).filter(Rol.nombre_rol.ilike(nombre)).first()
        if not rol:
            rol = Rol(nombre_rol=nombre)
            db.add(rol)
            db.commit()
            db.refresh(rol)
            print(f"  + Rol creado: {nombre} (id_rol={rol.id_rol})")
        else:
            print(f"  = Rol ya existía: {nombre} (id_rol={rol.id_rol})")
        roles[nombre] = rol
    return roles


def main():
    db = SessionLocal()
    try:
        print("1. Verificando/creando roles base...")
        roles = obtener_o_crear_roles(db)
        rol_admin = roles["administrador"]

        ya_existe_admin = (
            db.query(Usuario).filter(Usuario.id_rol == rol_admin.id_rol).first()
        )
        if ya_existe_admin:
            print(f"\nYa existe al menos un administrador ({ya_existe_admin.numero_documento}). Nada que hacer.")
            return

        print("\n2. Vamos a crear el primer administrador. Escribe sus datos:")
        nombre = input("  Nombre: ").strip()
        apellido = input("  Apellido (opcional): ").strip() or None
        numero_documento = input("  Número de documento: ").strip()
        tipo_documento = input("  Tipo de documento (ej. CC): ").strip()
        fecha_nacimiento_str = input("  Fecha de nacimiento (YYYY-MM-DD): ").strip()
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
        correo_personal = input("  Correo personal: ").strip()
        correo_sena = input("  Correo institucional (SENA): ").strip()
        contrasena = getpass.getpass("  Contraseña (mínimo 6 caracteres): ")

        nuevo_admin = Usuario(
            nombre=nombre,
            apellido=apellido,
            numero_documento=numero_documento,
            tipo_documento=tipo_documento,
            fecha_nacimiento=fecha_nacimiento,
            correo_personal=correo_personal,
            correo_sena=correo_sena,
            contrasena=hash_password(contrasena),
            id_rol=rol_admin.id_rol,
        )
        db.add(nuevo_admin)
        db.commit()
        print(f"\n✅ Administrador creado: {nombre} (documento {numero_documento}).")
        print("   Ya puedes hacer login con POST /api/v1/auth/login y usar ese token")
        print("   para crear más usuarios/administradores desde POST /api/usuarios.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
