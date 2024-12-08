import os
from sqlalchemy import text
from database import db
from models.usuario import Usuario
from models.ingrediente import Ingrediente
from models.producto import Producto
from flask import Flask
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Inicializar la aplicación Flask para usar SQLAlchemy
app = Flask(__name__)

# Configuración de la base de datos
uri = os.environ.get('DATABASE_URL')

# Reemplazar 'postgres://' por 'postgresql://' para compatibilidad con SQLAlchemy
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def poblar_base_de_datos():
    """
    Poblar la base de datos con usuarios, ingredientes y productos iniciales.
    """
    with app.app_context():
        try:
            db.create_all()  # Crear las tablas si no existen

            # Mostrar conteos actuales
            print(f"Usuarios existentes: {Usuario.query.count()}")
            print(f"Ingredientes existentes: {Ingrediente.query.count()}")
            print(f"Productos existentes: {Producto.query.count()}")

            # Crear usuarios iniciales
            usuarios_iniciales = [
                {"username": "admin", "password": "admin123", "es_admin": True, "es_empleado": False, "es_cliente": False},
                {"username": "empleado", "password": "empleado123", "es_admin": False, "es_empleado": True, "es_cliente": False},
                {"username": "cliente", "password": "cliente123", "es_admin": False, "es_empleado": False, "es_cliente": True},
            ]

            for usuario in usuarios_iniciales:
                if not Usuario.query.filter_by(username=usuario["username"]).first():
                    nuevo_usuario = Usuario(
                        username=usuario["username"],
                        es_admin=usuario["es_admin"],
                        es_empleado=usuario["es_empleado"],
                        es_cliente=usuario["es_cliente"]
                    )
                    nuevo_usuario.set_password(usuario["password"])
                    db.session.add(nuevo_usuario)
                    print(f"Usuario '{usuario['username']}' creado.")
                else:
                    print(f"Usuario '{usuario['username']}' ya existe.")

            db.session.commit()
            print("Usuarios iniciales procesados exitosamente.")

            # Crear ingredientes iniciales
            if Ingrediente.query.count() == 0:
                ingredientes = [
                    Ingrediente(nombre="Helado de Vainilla", precio=1000, calorias=150, inventario=20, es_vegetariano=True),
                    Ingrediente(nombre="Helado de Chocolate", precio=1200, calorias=200, inventario=20, es_vegetariano=True),
                    Ingrediente(nombre="Chispas de Chocolate", precio=500, calorias=50, inventario=30, es_vegetariano=True),
                    Ingrediente(nombre="Crema Chantilly", precio=300, calorias=120, inventario=40, es_vegetariano=True)
                ]

                db.session.add_all(ingredientes)
                db.session.commit()
                print("Ingredientes creados exitosamente.")

            # Crear productos iniciales
            if Producto.query.count() == 0:
                productos = [
                    Producto(
                        nombre="Copa Vainilla",
                        precio_publico=5000,
                        tipo="Copa",
                        ingrediente1_id=1,
                        ingrediente2_id=3,
                        ingrediente3_id=4
                    ),
                    Producto(
                        nombre="Copa Chocolate",
                        precio_publico=5500,
                        tipo="Copa",
                        ingrediente1_id=2,
                        ingrediente2_id=3,
                        ingrediente3_id=4
                    ),
                    Producto(
                        nombre="Malteada Vainilla",
                        precio_publico=6000,
                        tipo="Malteada",
                        ingrediente1_id=1,
                        ingrediente2_id=3,
                        ingrediente3_id=4
                    ),
                    Producto(
                        nombre="Malteada Chocolate",
                        precio_publico=6500,
                        tipo="Malteada",
                        ingrediente1_id=2,
                        ingrediente2_id=3,
                        ingrediente3_id=4
                    )
                ]

                db.session.add_all(productos)
                db.session.commit()
                print("Productos creados exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al poblar la base de datos: {e}")


if __name__ == '__main__':
    print("Poblando base de datos existente...")
    poblar_base_de_datos()
