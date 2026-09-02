from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.competencia import Competencia
from schemas.competencia import CompetenciaCreate

class CompetenciaService:
    def __init__(self, db: Session):
        self.db = db

    def crear_competencia(self, data_in: CompetenciaCreate):
        # Creamos la competencia
        nueva_competencia = Competencia(**data_in.model_dump())
        self.db.add(nueva_competencia)
        self.db.commit()
        self.db.refresh(nueva_competencia)
        return nueva_competencia

    def obtener_competencias(self):
        return self.db.query(Competencia).all()

    def obtener_competencia_por_id(self, id_competencia: int):
        competencia = self.db.query(Competencia).filter(Competencia.id_competencia == id_competencia).first()
        if not competencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Competencia no encontrada."
            )
        return competencia

    def actualizar_competencia(self, id_competencia: int, data_in: CompetenciaCreate):
        competencia_actual = self.obtener_competencia_por_id(id_competencia)
        
        competencia_actual.nombre = data_in.nombre
        competencia_actual.descripcion = data_in.descripcion
        competencia_actual.fecha_carga = data_in.fecha_carga
        
        self.db.commit()
        self.db.refresh(competencia_actual)
        return competencia_actual

    def eliminar_competencia(self, id_competencia: int):
        competencia = self.obtener_competencia_por_id(id_competencia)
        self.db.delete(competencia)
        self.db.commit()
        return {"mensaje": "Competencia eliminada correctamente."}
    