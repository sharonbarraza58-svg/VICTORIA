from sqlalchemy import Column, Integer, String, DateTime , ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class Ficha(Base):
    __tablename__ = 'ficha'

    id_ficha = Column(Integer, primary_key=True, autoincrement=True)
    estado = Column(String(10), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)

    # Llave foránea que conecta la ficha con su programa de formación.
    #
    # use_alter=True + name=... son necesarios porque hay una dependencia
    # circular real entre 'ficha' y 'programa': Ficha.id_programa apunta a
    # Programa, y Programa.id_ficha apunta de vuelta a Ficha. Sin
    # use_alter, Base.metadata.create_all() no sabe cuál de las dos tablas
    # crear primero y lanza CircularDependencyError en una base de datos
    # nueva. use_alter le dice a SQLAlchemy: "crea la columna primero, sin
    # la restricción, y añade la restricción FK después con un ALTER TABLE"
    # -- exactamente lo mismo que ya hace el script SQL a mano.
    id_programa = Column(
        Integer,
        ForeignKey('programa.id_programa', ondelete="SET NULL", use_alter=True, name="fk_ficha_programa"),
        nullable=True,
    )

    # Instructor responsable de la ficha. La columna ya existe en scriptposgrest.
    id_usuario = Column(
        Integer,
        ForeignKey('usuario.id_usuario', ondelete="SET NULL", use_alter=True, name="fk_ficha_instructor"),
        nullable=True,
    )

    # NOTA: el script SQL también agrega, vía ALTER TABLE, las columnas
    # id_proyecto, id_usuario, id_material e id_evidencia en 'ficha'. No se
    # mapean aquí porque ningún endpoint de la API las usa todavía (ver
    # schemas/ficha.py y services/ficha_service.py) y varias de ellas caen
    # en ciclos de dependencia más largos (Ficha -> Evidencia -> Entregable
    # -> Cronograma -> Ficha). Si en el futuro se necesitan desde la API,
    # se pueden agregar igual que id_programa: con use_alter=True.

       # Relaciones
    usuarios = relationship(
        "Usuario",
        back_populates="ficha",
        foreign_keys="Usuario.id_ficha"
    )

    programa = relationship(
        "Programa",
        back_populates="fichas",
        foreign_keys=[id_programa]
    )