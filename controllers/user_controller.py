from flask import Blueprint, request, jsonify, abort, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models.usuario import Usuario

user_bp = Blueprint('user', __name__, url_prefix='/api/usuarios')

class UserController:
    @staticmethod
    @user_bp.route('/register', methods=['POST'])
    def register():
        """Registra un nuevo usuario."""
        data = request.get_json()  # Cambiar a request.json para JSON más limpio
        if not data:
            abort(400, description="No se proporcionaron datos.")

        username = data.get('username')
        password = data.get('password')
        es_admin = data.get('es_admin', False)
        es_empleado = data.get('es_empleado', False)
        es_cliente = data.get('es_cliente', True)  # Por defecto, es cliente

        if not username or not password:
            abort(400, description="Faltan datos obligatorios (username y password).")

        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            abort(400, description="El nombre de usuario ya está registrado.")

        # Crear un nuevo usuario
        usuario = Usuario(
            username=username,
            es_admin=es_admin,
            es_empleado=es_empleado,
            es_cliente=es_cliente
        )
        usuario.set_password(password)

        # Guardar en la base de datos
        db.session.add(usuario)
        db.session.commit()

        return jsonify({"message": "Usuario registrado exitosamente.", "username": username}), 201

    @staticmethod
    @user_bp.route('/login', methods=['POST'])
    def login():
        data = request.form
        username = data.get('username')
        password = data.get('password')

        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario or not usuario.check_password(password):
            flash("Credenciales inválidas.", "error")
            return redirect(url_for('routes.root'))

        login_user(usuario)
        flash("Inicio de sesión exitoso.", "success")
        return redirect(url_for('routes.root'))

    # Verifica que ambos campos estén presentes
        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "error")
            return redirect(url_for('routes.root'))

    # Busca al usuario en la base de datos
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario or not usuario.check_password(password):
            flash("Credenciales incorrectas.", "error")
            return redirect(url_for('routes.root'))

    # Autentica al usuario
        login_user(usuario)
        flash("Inicio de sesión exitoso.", "success")
        return redirect(url_for('routes.index'))  # Redirige a la página principal


    @staticmethod
    @user_bp.route('/perfil', methods=['GET'])
    @login_required
    def perfil():
        """Devuelve la información del usuario actual."""
        return jsonify({
            "id": current_user.id,
            "username": current_user.username,
            "es_admin": current_user.es_admin,
            "es_empleado": current_user.es_empleado,
            "es_cliente": current_user.es_cliente
        }), 200

@staticmethod
@user_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    """Cierra la sesión del usuario actual."""
    logout_user()
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('routes.root'))
