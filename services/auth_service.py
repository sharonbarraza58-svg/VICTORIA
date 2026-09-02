from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.usuario import Usuario
from models.rol import Rol
from schemas.usuario import UsuarioRegistroPublico
from core.security import hash_password, verify_password

# Nombre del rol que se le asigna a TODO el que se registra por la ruta
# pública (POST /api/v1/auth/register). No es negociable por el cliente:
# ver la explicación completa en schemas/usuario.py, junto a
# UsuarioRegistroPublico.
ROL_PUBLICO_POR_DEFECTO = "aprendiz"


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def registrar_usuario(self, user_in: UsuarioRegistroPublico):
        """Registra un nuevo usuario por la vía PÚBLICA (sin sesión), encriptando
        su contraseña y asignándole SIEMPRE el rol seguro por defecto
        (ROL_PUBLICO_POR_DEFECTO). El cliente no puede elegir su propio rol acá;
        para crear administradores/instructores existe POST /api/usuarios,
        que sí exige estar autenticado como administrador."""
        # 1. Verificamos que el documento no esté ya registrado
        existe_doc = self.db.query(Usuario).filter(Usuario.numero_documento == user_in.numero_documento).first()
        if existe_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de documento ya se encuentra registrado."
            )

        # 2. Buscamos el rol seguro por defecto. Si todavía no existe (por
        #    ejemplo, en una base de datos recién creada donde nadie ha
        #    llamado a POST /api/roles), no dejamos pasar el registro con un
        #    id_rol inventado: es mejor un error claro que un usuario mal
        #    formado en la base de datos.
        rol_por_defecto = (
            self.db.query(Rol)
            .filter(Rol.nombre_rol.ilike(ROL_PUBLICO_POR_DEFECTO))
            .first()
        )
        if not rol_por_defecto:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"No existe el rol '{ROL_PUBLICO_POR_DEFECTO}' en la base de datos. "
                    "Un administrador debe crearlo primero con POST /api/roles."
                ),
            )

        # 3. Encriptamos la contraseña
        password_segura = hash_password(user_in.contrasena)

        # 4. Preparamos el usuario para guardarlo. id_rol SIEMPRE sale de
        #    rol_por_defecto.id_rol, nunca de algo que mandó el cliente.
        nuevo_usuario = Usuario(
            nombre=user_in.nombre,
            apellido=user_in.apellido,
            tipo_documento=user_in.tipo_documento,
            numero_documento=user_in.numero_documento,
            fecha_nacimiento=user_in.fecha_nacimiento,
            telefono=user_in.telefono,
            correo_personal=user_in.correo_personal,
            correo_sena=user_in.correo_sena,
            contrasena=password_segura,  # Guardamos el hash, NUNCA la clave plana
            id_ficha=user_in.id_ficha,
            id_coordinacion=user_in.id_coordinacion,
            id_rol=rol_por_defecto.id_rol,
        )

        # 5. Guardamos en la Base de Datos
        self.db.add(nuevo_usuario)
        self.db.commit()
        self.db.refresh(nuevo_usuario)

        return nuevo_usuario

    def autenticar_usuario(self, numero_documento: str, password_plana: str):
        """Busca al usuario por documento y verifica si la clave cuadra."""
        usuario = self.db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()

        if not usuario:
            return False

        if not verify_password(password_plana, usuario.contrasena):
            return False

        return usuario