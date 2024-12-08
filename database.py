from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """
    Inicializa SQLAlchemy con la aplicación Flask.
    No intenta crear la base de datos porque Heroku ya la proporciona.
    """
    db.init_app(app)
