from database import db

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio_publico = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    ingrediente1_id = db.Column(db.Integer, db.ForeignKey('ingredientes.id'), nullable=False)
    ingrediente2_id = db.Column(db.Integer, db.ForeignKey('ingredientes.id'), nullable=False)
    ingrediente3_id = db.Column(db.Integer, db.ForeignKey('ingredientes.id'), nullable=False)

    ingrediente1 = db.relationship('Ingrediente', foreign_keys=[ingrediente1_id])
    ingrediente2 = db.relationship('Ingrediente', foreign_keys=[ingrediente2_id])
    ingrediente3 = db.relationship('Ingrediente', foreign_keys=[ingrediente3_id])

    def __repr__(self):
        return f"<Producto {self.nombre}>"

    def calcular_rentabilidad(self):
        """
        Calcula la rentabilidad del producto como la diferencia entre el precio público
        y el costo de los ingredientes.
        """
        costo_ingredientes = (
            self.ingrediente1.precio +
            self.ingrediente2.precio +
            self.ingrediente3.precio
        )
        rentabilidad = self.precio_publico - costo_ingredientes
        return rentabilidad

    def to_dict(self):
        """
        Convierte el objeto Producto en un diccionario para representación JSON.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio_publico": self.precio_publico,
            "tipo": self.tipo,
            "ingredientes": [
                self.ingrediente1.to_dict(),
                self.ingrediente2.to_dict(),
                self.ingrediente3.to_dict()
            ]
        }
