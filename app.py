import os
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
from database import db, init_db  # Importar la instancia de la base de datos
from models.usuario import Usuario
from controllers.routes_controller import routes_bp  # Importar el Blueprint de rutas
from controllers.api_controller import api_bp  # Importar el Blueprint de API
from controllers.user_controller import user_bp  # Importar el Blueprint de usuarios

# Cargar configuración desde .env
load_dotenv()

# Inicializar la aplicación y especificar la carpeta de templates
app = Flask(__name__, template_folder='views')

# Configuración de la base de datos
uri = os.environ.get('DATABASE_URL')  # URL proporcionada por Heroku

# Reemplazar 'postgres://' por 'postgresql://' si es necesario
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

# Configurar SQLAlchemy con la URI de la base de datos corregida
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar la clave secreta para la aplicación
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_predeterminada')

# Inicializar la base de datos y migraciones
init_db(app)
migrate = Migrate(app, db)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.root'  # Ruta para el login (puedes cambiar a 'routes.login' si /login es la ruta real)

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos por su ID."""
    return Usuario.query.get(int(user_id))

# Registrar Blueprints
app.register_blueprint(routes_bp)  # Sin prefijo para permitir que '/' sea manejado por este Blueprint
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api/usuarios')

if __name__ == '__main__':
    app.run(debug=True)
