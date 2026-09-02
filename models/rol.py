from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, index=True)

    # IMPORTANTE:
    # En PostgreSQL la columna se llama "nombre", NO "nombre_rol"
    nombre = Column(String(50), nullable=False)

    descripcion = Column(String, nullable=True)

    usuarios = relationship(
        "Usuario",
        back_populates="rol"
    )