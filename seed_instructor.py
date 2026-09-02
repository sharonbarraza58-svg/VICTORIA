"""Crea los roles base y un instructor de prueba en PostgreSQL.

Uso:
    python seed_instructor.py

El script no guarda la contraseña en texto plano: usa el mismo hash PBKDF2
que utiliza el login de VICTORIA.
"""
import getpass
from datetime import datetime

from db.database import SessionLocal, Base, engine
import models  # noqa: F401
from models.rol import Rol
from models.usuario import Usuario
from core.security import hash_password

ROLES_BASE = ["administrador", "instructor", "coordinador", "aprendiz"]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        roles = {}
        for nombre in ROLES_BASE:
            rol = db.query(Rol).filter(Rol.nombre_rol.ilike(nombre)).first()
            if not rol:
                rol = Rol(nombre_rol=nombre)
                db.add(rol)
                db.commit()
                db.refresh(rol)
            roles[nombre] = rol

        documento = input("Número de documento del instructor: ").strip()
        existente = db.query(Usuario).filter(Usuario.numero_documento == documento).first()
        if existente:
            print(f"Ya existe el usuario {existente.nombre} ({existente.numero_documento}).")
            print(f"Rol actual: {existente.rol_nombre}")
            return

        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip() or None
        tipo_documento = input("Tipo de documento (CC/TI/etc.): ").strip() or "CC"
        fecha_nacimiento = datetime.strptime(
            input("Fecha de nacimiento (YYYY-MM-DD): ").strip(), "%Y-%m-%d"
        ).date()
        correo_personal = input("Correo personal: ").strip()
        correo_sena = input("Correo SENA: ").strip()
        telefono = input("Teléfono (opcional): ").strip() or None
        contrasena = getpass.getpass("Contraseña (mínimo 6 caracteres): ")
        if len(contrasena) < 6:
            raise SystemExit("La contraseña debe tener mínimo 6 caracteres.")

        instructor = Usuario(
            nombre=nombre,
            apellido=apellido,
            id_rol=roles["instructor"].id_rol,
            correo_personal=correo_personal,
            correo_sena=correo_sena,
            tipo_documento=tipo_documento,
            numero_documento=documento,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            contrasena=hash_password(contrasena),
            estado="activo",
        )
        db.add(instructor)
        db.commit()
        db.refresh(instructor)
        print("\nInstructor creado correctamente.")
        print(f"ID: {instructor.id_usuario}")
        print(f"Documento para login: {instructor.numero_documento}")
        print("Rol: instructor")
    finally:
        db.close()


if __name__ == "__main__":
    main()
