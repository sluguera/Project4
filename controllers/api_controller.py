from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_user
from database import db
from models.ingrediente import Ingrediente
from models.producto import Producto
from models.usuario import Usuario

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Decoradores para autorización
def admin_required(func):
    """Restringe el acceso a administradores."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_admin:
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def employee_required(func):
    """Permite el acceso a empleados y administradores (excluye funciones de rentabilidad)."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.es_empleado and not current_user.es_admin):
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def client_required(func):
    """Permite el acceso a clientes y administradores."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.es_cliente and not current_user.es_admin):
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


class APIController:
    @staticmethod
    @api_bp.route('/login', methods=['POST'])
    def login_api():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario or not usuario.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        login_user(usuario)  # Establece current_user
        return jsonify({
            "message": "Login successful.",
            "username": usuario.username,
            "es_admin": usuario.es_admin,
            "es_empleado": usuario.es_empleado,
            "es_cliente": usuario.es_cliente
        }), 200

    @staticmethod
    @api_bp.route('/productos', methods=['GET'])
    def consultar_todos_productos():
        """Consulta todos los productos (acceso público)."""
        productos = Producto.query.all()
        return jsonify([p.to_dict() for p in productos]), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>', methods=['GET'])
    @client_required
    def consultar_producto_por_id(producto_id):
        """Consulta un producto por su ID."""
        producto = Producto.query.get_or_404(producto_id)
        return jsonify(producto.to_dict()), 200

    @staticmethod
    @api_bp.route('/productos/nombre/<string:nombre>', methods=['GET'])
    @client_required
    def consultar_producto_por_nombre(nombre):
        """Consulta un producto por su nombre."""
        producto = Producto.query.filter_by(nombre=nombre).first()
        if not producto:
            abort(404, description="Producto no encontrado.")
        return jsonify(producto.to_dict()), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>/calorias', methods=['GET'])
    @client_required
    def consultar_calorias_producto(producto_id):
        """Consulta las calorías de un producto."""
        producto = Producto.query.get_or_404(producto_id)
        calorias = (
            producto.ingrediente1.calorias +
            producto.ingrediente2.calorias +
            producto.ingrediente3.calorias
        )
        return jsonify({"producto": producto.nombre, "calorias": calorias}), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>/rentabilidad', methods=['GET'])
    @admin_required
    def consultar_rentabilidad_producto(producto_id):
        """Consulta la rentabilidad de un producto."""
        producto = Producto.query.get_or_404(producto_id)
        rentabilidad = producto.precio_publico - (
            producto.ingrediente1.precio +
            producto.ingrediente2.precio +
            producto.ingrediente3.precio
        )
        return jsonify({"producto": producto.nombre, "rentabilidad": rentabilidad}), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>/costo', methods=['GET'])
    @admin_required
    def consultar_costo_produccion_producto(producto_id):
        """Consulta el costo de producción de un producto."""
        producto = Producto.query.get_or_404(producto_id)
        costo = (
            producto.ingrediente1.precio +
            producto.ingrediente2.precio +
            producto.ingrediente3.precio
        )
        return jsonify({"producto": producto.nombre, "costo_produccion": costo}), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>/vender', methods=['POST'])
    @client_required
    def vender_producto(producto_id):
        """Vende un producto."""
        producto = Producto.query.get_or_404(producto_id)
        for ingrediente in [producto.ingrediente1, producto.ingrediente2, producto.ingrediente3]:
            if ingrediente.inventario < 1:
                abort(400, description=f"Sin stock para: {ingrediente.nombre}")
            ingrediente.inventario -= 1

        db.session.commit()
        return jsonify({"message": f"Producto '{producto.nombre}' vendido exitosamente."}), 200

    @staticmethod
    @api_bp.route('/ingredientes', methods=['GET'])
    @employee_required
    def consultar_todos_ingredientes():
        """Consulta todos los ingredientes."""
        ingredientes = Ingrediente.query.all()
        return jsonify([i.to_dict() for i in ingredientes]), 200

    @staticmethod
    @api_bp.route('/ingredientes/<int:ingrediente_id>', methods=['GET'])
    @employee_required
    def consultar_ingrediente_por_id(ingrediente_id):
        """Consulta un ingrediente por su ID."""
        ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
        return jsonify(ingrediente.to_dict()), 200

    @staticmethod
    @api_bp.route('/ingredientes/nombre/<string:nombre>', methods=['GET'])
    @employee_required
    def consultar_ingrediente_por_nombre(nombre):
        """Consulta un ingrediente por su nombre."""
        ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
        if not ingrediente:
            abort(404, description="Ingrediente no encontrado.")
        return jsonify(ingrediente.to_dict()), 200

    @staticmethod
    @api_bp.route('/ingredientes/<int:ingrediente_id>/sano', methods=['GET'])
    @client_required
    def es_ingrediente_sano(ingrediente_id):
        """Consulta si un ingrediente es sano."""
        ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
        es_sano = ingrediente.es_vegetariano and ingrediente.calorias < 100
        return jsonify({"ingrediente": ingrediente.nombre, "es_sano": es_sano}), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>/reabastecer', methods=['POST'])
    @employee_required
    def reabastecer_producto(producto_id):
        """Reabastece un producto."""
        data = request.get_json()
        cantidad = data.get('cantidad')
        if not cantidad or cantidad <= 0:
            abort(400, description="Cantidad inválida para reabastecimiento.")

        producto = Producto.query.get_or_404(producto_id)
        for ingrediente in [producto.ingrediente1, producto.ingrediente2, producto.ingrediente3]:
            ingrediente.inventario += cantidad

        db.session.commit()
        return jsonify({"message": f"Producto '{producto.nombre}' reabastecido en {cantidad} unidades."}), 200

    @staticmethod
    @api_bp.route('/productos/<int:producto_id>/renovar', methods=['POST'])
    @employee_required
    def renovar_inventario_producto(producto_id):
        """Renueva el inventario de un producto."""
        producto = Producto.query.get_or_404(producto_id)
        for ingrediente in [producto.ingrediente1, producto.ingrediente2, producto.ingrediente3]:
            ingrediente.inventario = 50

        db.session.commit()
        return jsonify({"message": f"Inventario de '{producto.nombre}' renovado exitosamente."}), 200
