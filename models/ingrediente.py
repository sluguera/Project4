from database import db

class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    inventario = db.Column(db.Integer, nullable=False)
    es_vegetariano = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Ingrediente {self.nombre}>"

    def to_dict(self):
        """
        Convierte el objeto Ingrediente en un diccionario para representación JSON.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "calorias": self.calorias,
            "inventario": self.inventario,
            "es_vegetariano": self.es_vegetariano
        }
