from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import current_user, login_required
from controllers.heladeria_controller import HeladeriaController
from controllers.decorators import role_required, public_access
from database import db
from models.producto import Producto
from models.usuario import Usuario

# Crear el Blueprint para las rutas
routes_bp = Blueprint('routes', __name__)

# Instancia del controlador
heladeria_controller = HeladeriaController()

@routes_bp.route('/')
def root():
    """
    Redirige al formulario de inicio de sesión o a la página principal protegida.
    """
    if current_user.is_authenticated:
        # Redirige a la página principal si el usuario ya está autenticado
        return redirect(url_for('routes.index'))
    # Muestra el formulario de login si no está autenticado
    return render_template('login.html')

@routes_bp.route('/index')
@login_required
def index():
    """
    Muestra la página principal con la lista de productos.
    """
    try:
        productos = Producto.query.options(
            db.joinedload(Producto.ingrediente1),
            db.joinedload(Producto.ingrediente2),
            db.joinedload(Producto.ingrediente3)
        ).all()

        if not productos:
            flash("No hay productos disponibles en este momento.", "info")

        return render_template('index.html', productos=productos)
    except Exception as e:
        flash("Error al cargar los productos.", "error")
        print(f"Error en la ruta /index: {e}")
        return redirect(url_for('user.login'))


@routes_bp.route('/listar-productos')
@public_access  # Acceso público
def listar_productos():
    """Lista los productos disponibles."""
    return heladeria_controller.listar_productos()

@routes_bp.route('/vender/<int:producto_id>', methods=['POST'])
@login_required
@role_required('cliente')  # Clientes y administradores
def vender(producto_id):
    """
    Maneja la venta de un producto. Captura errores específicos y muestra mensajes flash.
    """
    return heladeria_controller.manejar_venta(producto_id)

@routes_bp.route('/resumen-ventas')
@login_required
@role_required('empleado')  # Empleados y administradores
def resumen_ventas():
    """
    Muestra el resumen de ventas realizadas.
    """
    return heladeria_controller.mostrar_resumen_ventas()

@routes_bp.route('/producto-mas-rentable')
@login_required
@role_required('admin')  # Solo administradores
def producto_mas_rentable():
    """
    Calcula y muestra el producto más rentable.
    """
    return heladeria_controller.producto_mas_rentable()

@routes_bp.route('/inventario')
def mostrar_inventario():
    """
    Muestra el inventario actual de ingredientes.
    """
    return heladeria_controller.mostrar_inventario()

@routes_bp.route('/recargar-inventario/<int:ingrediente_id>', methods=['POST'])
def recargar_inventario(ingrediente_id):
    """
    Recarga el inventario de un ingrediente específico.
    """
    try:
        cantidad = int(request.form['cantidad'])  # Captura la cantidad enviada por el formulario
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        return heladeria_controller.recargar_inventario(ingrediente_id, cantidad)
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('routes.mostrar_inventario'))

@routes_bp.route('/verificar-inventario-bajo')
def verificar_inventario_bajo():
    """
    Verifica los ingredientes con inventario bajo y genera alertas.
    """
    return heladeria_controller.verificar_inventario_bajo()

@routes_bp.route('/web-register', methods=['GET', 'POST'])
def web_register():
    """Formulario de registro web para clientes."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "error")
            return redirect(url_for('routes.web_register'))

        if Usuario.query.filter_by(username=username).first():
            flash("El usuario ya existe. Prueba con otro nombre.", "error")
            return redirect(url_for('routes.web_register'))

        # Crear usuario como cliente
        usuario = Usuario(
            username=username,
            es_cliente=True,  # Siempre cliente
            es_admin=False,
            es_empleado=False
        )
        usuario.set_password(password)

        db.session.add(usuario)
        db.session.commit()

        flash("Usuario registrado exitosamente.", "success")
        return redirect(url_for('routes.root'))  # Redirigir al login

    return render_template('register.html')  # Muestra el template de registro

@routes_bp.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403
