from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.ficha import Ficha  # Asegúrate de que la importación coincida con tu archivo
from schemas.ficha import FichaCreate

class FichaService:
    def __init__(self, db: Session):
        self.db = db

    def crear_ficha(self, data_in: FichaCreate):
        # Aquí la base de datos validará automáticamente que el id_programa exista
        # gracias a la llave foránea.
        nueva_ficha = Ficha(**data_in.model_dump())
        self.db.add(nueva_ficha)
        self.db.commit()
        self.db.refresh(nueva_ficha)
        return nueva_ficha

    def obtener_fichas(self):
        return self.db.query(Ficha).all()

    def obtener_ficha_por_id(self, id_ficha: int):
        ficha = self.db.query(Ficha).filter(Ficha.id_ficha == id_ficha).first()
        if not ficha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Ficha no encontrada."
            )
        return ficha

    def actualizar_ficha(self, id_ficha: int, data_in: FichaCreate):
        ficha_actual = self.obtener_ficha_por_id(id_ficha)
        
        # Actualizamos los campos
        ficha_actual.estado = data_in.estado
        ficha_actual.fecha_inicio = data_in.fecha_inicio
        ficha_actual.fecha_fin = data_in.fecha_fin
        ficha_actual.id_programa = data_in.id_programa
        
        self.db.commit()
        self.db.refresh(ficha_actual)
        return ficha_actual

    def eliminar_ficha(self, id_ficha: int):
        ficha = self.obtener_ficha_por_id(id_ficha)
        self.db.delete(ficha)
        self.db.commit()
        return {"mensaje": "Ficha eliminada exitosamente."}
    