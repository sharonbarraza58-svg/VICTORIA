from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from db.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    nombre = Column(String(100), nullable=False)

    apellido = Column(String(100), nullable=True)

    id_rol = Column(
        Integer,
        ForeignKey("rol.id_rol"),
        nullable=False
    )

    fecha_creacion = Column(
        DateTime,
        default=datetime.utcnow
    )

    estado = Column(
        String(50),
        default="activo"
    )

    fecha_nacimiento = Column(
        Date,
        nullable=False
    )

    numero_documento = Column(
        String(20),
        unique=True,
        nullable=False
    )

    tipo_documento = Column(
        String(20),
        nullable=False
    )

    telefono = Column(
        String(20),
        nullable=True
    )

    correo_personal = Column(
        String(100),
        unique=True,
        nullable=False
    )

    correo_sena = Column(
        String(100),
        unique=True,
        nullable=False
    )

    contrasena = Column(
        String(255),
        nullable=False
    )

    id_ficha = Column(
        Integer,
        ForeignKey(
            "ficha.id_ficha",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    id_coordinacion = Column(
        Integer,
        ForeignKey(
            "coordinacion.id_coordinacion",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    # Relación con Rol
    rol = relationship(
        "Rol",
        back_populates="usuarios"
    )

    # Relación con Ficha
    ficha = relationship(
        "Ficha",
        back_populates="usuarios",
        foreign_keys=[id_ficha]
    )

    @property
    def rol_nombre(self):
        return self.rol.nombre if self.rol else None