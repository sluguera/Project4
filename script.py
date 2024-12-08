from database import db
from app import app  # Asegúrate de que la instancia de tu aplicación esté importada

with app.app_context():
    db.drop_all()  # Borra todas las tablas
    db.create_all()  # Crea las tablas nuevamente según tus modelos
