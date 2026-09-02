from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from db.database import Base

class Competencia(Base):
    __tablename__ = 'competencia'

    id_competencia = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(String(300), nullable=True)
    fecha_carga = Column(DateTime, nullable=False)

    id_programa = Column(Integer, ForeignKey('programa.id_programa'), nullable=True)

    # NOTA: el script agrega, vía ALTER TABLE, dos columnas más en
    # competencia: id_programa e id_resultado. No se mapean aquí:
    # - id_programa crearía una segunda llave foránea circular entre
    #   'competencia' y 'programa' (Programa ya tiene su propio
    #   id_competencia); no la necesita ningún endpoint hoy.
    # - id_resultado apunta a 'resultado_aprendizaje', tabla que no forma
    #   parte de este recorte de 8 tablas -- mapearla haría que la app
    #   fallara al arrancar (Base.metadata.create_all() no encuentra esa
    #   tabla en el registro de modelos).