from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user
from datetime import datetime
from database import db
from models.ingrediente import Ingrediente
from models.producto import Producto


class HeladeriaController:
    def __init__(self):
        """
        Inicializa la clase con una lista para registrar las ventas realizadas.
        """
        if not hasattr(HeladeriaController, 'ventas'):
            # Lista compartida entre todas las instancias de HeladeriaController
            HeladeriaController.ventas = []
            
    def listar_productos(self):
        """
        Obtiene todos los productos disponibles desde la base de datos.
        """
        try:
            productos = Producto.query.options(
                db.joinedload(Producto.ingrediente1),
                db.joinedload(Producto.ingrediente2),
                db.joinedload(Producto.ingrediente3)
            ).all()

            if not productos:
                flash("No hay productos disponibles en este momento.", "info")
                productos = []

        # Imprime los productos para depuración
            for producto in productos:
                print(
                    f"Producto: {producto.nombre}, Precio: {producto.precio_publico}, "
                    f"Ingrediente1: {producto.ingrediente1.nombre}, "
                    f"Ingrediente2: {producto.ingrediente2.nombre}, "
                    f"Ingrediente3: {producto.ingrediente3.nombre}"
                )

            return render_template('listar_productos.html', productos=productos)
        except Exception as e:
            flash("Error al listar los productos.", "error")
            print(f"Error en listar_productos: {e}")
            raise


    def manejar_venta(self, producto_id):
        """
        Maneja el proceso de venta, capturando posibles errores y retornando mensajes apropiados.
        """
        try:
            mensaje = self.vender_producto(producto_id)
            flash(mensaje, "success")
        except ValueError as ve:
            # Si ocurre un ValueError, retorna un mensaje personalizado
            flash(f"¡Oh no! Nos hemos quedado sin {ve}.", "error")
        except Exception as e:
            # Manejo de cualquier otro error
            flash("Ha ocurrido un error inesperado al intentar realizar la venta.", "error")
            print(f"Error en manejar_venta: {e}")
        return redirect(url_for('routes.index'))

    def mostrar_resumen_ventas(self):
        """
        Retorna el resumen de ventas basado en la lista de memoria.
        """
        try:
            return render_template('resumen_ventas.html', ventas=HeladeriaController.ventas)
        except Exception as e:
            flash("Error al mostrar el resumen de ventas.", "error")
            print(f"Error en mostrar_resumen_ventas: {e}")  # Para depuración
            raise

    def producto_mas_rentable(self):
        """
        Encuentra y muestra el producto más rentable, incluyendo el costo de producción.
        """
        if not current_user.es_admin:
            abort(403)
        try:
            productos = Producto.query.options(
                db.joinedload(Producto.ingrediente1),
                db.joinedload(Producto.ingrediente2),
                db.joinedload(Producto.ingrediente3)
                ).all()

            if not productos:
                raise ValueError("No hay productos disponibles para calcular rentabilidad.")

        # Calcular el producto más rentable
            producto_rentable = max(productos, key=lambda p: p.calcular_rentabilidad())
            rentabilidad = producto_rentable.calcular_rentabilidad()

        # Calcular el costo de producción
            costo_produccion = (
                producto_rentable.ingrediente1.precio +
                producto_rentable.ingrediente2.precio +
                producto_rentable.ingrediente3.precio)

            return render_template(
                'producto_rentable.html',
                producto=producto_rentable,
                rentabilidad=rentabilidad,
                costo_produccion=costo_produccion)
        except ValueError as ve:
            flash(str(ve), "error")
            return redirect(url_for('routes.index'))  # Redirigir si no hay productos disponibles
        except Exception as e:
            flash("Error al calcular el producto más rentable.", "error")
            print(f"Error en producto_mas_rentable: {e}")  # Para depuración
            return redirect(url_for('routes.index'))


    def mostrar_inventario(self):
        """
        Obtiene el inventario actual de ingredientes.
        """
        try:
            ingredientes = Ingrediente.query.all()
            return render_template('inventario.html', ingredientes=ingredientes)
        except Exception as e:
            flash("Error al mostrar el inventario.", "error")
            print(f"Error en mostrar_inventario: {e}")  # Para depuración
            raise

    def recargar_inventario(self, ingrediente_id, cantidad):
        """
        Recarga el inventario de un ingrediente en específico.
        """
        try:
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0.")

            ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
            ingrediente.inventario += cantidad
            db.session.commit()
            flash(f"Inventario de '{ingrediente.nombre}' recargado en {cantidad} unidades.", "success")
        except ValueError as ve:
            flash(str(ve), "error")
            raise
        except Exception as e:
            flash("Error al recargar el inventario.", "error")
            print(f"Error en recargar_inventario: {e}")  # Para depuración
            raise
        return redirect(url_for('routes.mostrar_inventario'))

    def verificar_inventario_bajo(self):
        """
        Verifica si hay ingredientes con inventario bajo y muestra alertas.
        """
        try:
            UMBRAL_INVENTARIO_BAJO = 5

            # Obtener los ingredientes con inventario por debajo del umbral
            ingredientes_bajos = Ingrediente.query.filter(Ingrediente.inventario < UMBRAL_INVENTARIO_BAJO).all()

            if ingredientes_bajos:
                for ingrediente in ingredientes_bajos:
                    flash(f"El inventario de '{ingrediente.nombre}' es bajo: {ingrediente.inventario} unidades.", "warning")
            else:
                flash("Todos los ingredientes tienen inventario suficiente.", "success")
        except Exception as e:
            flash("Error al verificar inventario bajo.", "error")
            print(f"Error en verificar_inventario_bajo: {e}")  # Para depuración
            raise
        return redirect(url_for('routes.mostrar_inventario'))

# Consultar todos los productos
    def consultar_todos_productos(self):
            """
            Obtiene todos los productos disponibles.
            """
            try:
                productos = Producto.query.all()
                return productos
            except Exception as e:
                print(f"Error al consultar todos los productos: {e}")
                raise

# Consultar un producto según su ID
    def consultar_producto_por_id(self, producto_id):
        """
        Obtiene un producto según su ID.
        """
        try:
            producto = Producto.query.get_or_404(producto_id)
            return producto
        except Exception as e:
            print(f"Error al consultar el producto por ID: {e}")
            raise
    
# Consultar un producto según su nombre
    def consultar_producto_por_nombre(self, nombre):
        """
        Obtiene un producto según su nombre.
        """
        try:
            producto = Producto.query.filter_by(nombre=nombre).first()
            if not producto:
                raise ValueError(f"No se encontró un producto con el nombre '{nombre}'.")
            return producto
        except Exception as e:
            print(f"Error al consultar el producto por nombre: {e}")
            raise
    
# Consultar las calorías de un producto según su ID
    def consultar_calorias_producto(self, producto_id):
        """
        Obtiene las calorías totales de un producto según su ID.
        """
        try:
            producto = Producto.query.get_or_404(producto_id)
            calorias_totales = (
            producto.ingrediente1.calorias +
            producto.ingrediente2.calorias +
            producto.ingrediente3.calorias
            )
            return calorias_totales
        except Exception as e:
            print(f"Error al consultar las calorías del producto: {e}")
            raise
    
# Consultar la rentabilidad de un producto según su ID
    def consultar_rentabilidad_producto(self, producto_id):
        """
        Calcula la rentabilidad de un producto según su ID.
        """
        try:
            producto = Producto.query.get_or_404(producto_id)
            rentabilidad = producto.precio_publico - (
            producto.ingrediente1.precio +
            producto.ingrediente2.precio +
            producto.ingrediente3.precio
        )
            return rentabilidad
        except Exception as e:
            print(f"Error al consultar la rentabilidad del producto: {e}")
            raise

# Consultar el costo de producción de un producto según su ID
    def consultar_costo_produccion_producto(self, producto_id):
        """
        Calcula el costo de producción de un producto según su ID.
        """
        try:
            producto = Producto.query.get_or_404(producto_id)
            costo_produccion = (
                producto.ingrediente1.precio +
                producto.ingrediente2.precio +
                producto.ingrediente3.precio
            )
            return costo_produccion
        except Exception as e:
            print(f"Error al consultar el costo de producción del producto: {e}")
            raise
    
# Vender un producto según su ID
    def vender_producto(self, producto_id):
            """
            Gestiona la venta de un producto por su ID.
            Retorna:
            - "¡Vendido!" si la venta fue exitosa.
            - ValueError con el nombre del ingrediente si no se cumple la regla de venta.
            """
            producto = Producto.query.get_or_404(producto_id)
    
            # Verificar disponibilidad de ingredientes
            if producto.ingrediente1.inventario < 1:
                raise ValueError(producto.ingrediente1.nombre)
            if producto.ingrediente2.inventario < 1:
                raise ValueError(producto.ingrediente2.nombre)
            if producto.ingrediente3.inventario < 1:
                raise ValueError(producto.ingrediente3.nombre)
    
            # Reducir inventarios
            producto.ingrediente1.inventario -= 1
            producto.ingrediente2.inventario -= 1
            producto.ingrediente3.inventario -= 1
    
            # Registrar la venta en memoria
            HeladeriaController.ventas.append({
                'producto': producto.nombre,
                'precio': producto.precio_publico,
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
            # Guardar los cambios en la base de datos
            db.session.commit()
            return "¡Vendido!"
    
# Consultar todos los ingredientes
    def consultar_todos_ingredientes(self):
        """
        Obtiene todos los ingredientes disponibles.
        """
        try:
            ingredientes = Ingrediente.query.all()
            return ingredientes
        except Exception as e:
            print(f"Error al consultar todos los ingredientes: {e}")
            raise
    
# Consultar un ingrediente según su ID
    def consultar_ingrediente_por_id(self, ingrediente_id):
        """
        Obtiene un ingrediente según su ID.
        """
        try:
            ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
            return ingrediente
        except Exception as e:
            print(f"Error al consultar el ingrediente por ID: {e}")
            raise

# Consultar un ingrediente según su nombre
    def consultar_ingrediente_por_nombre(self, nombre):
        """
        Obtiene un ingrediente según su nombre.
        """
        try:
            ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
            if not ingrediente:
                raise ValueError(f"No se encontró un ingrediente con el nombre '{nombre}'.")
            return ingrediente
        except Exception as e:
            print(f"Error al consultar el ingrediente por nombre: {e}")
            raise

# Consultar si un ingrediente es sano según su ID
    def es_ingrediente_sano(self, ingrediente_id):
        """
        Verifica si un ingrediente es sano (es vegetariano y bajo en calorías).
        """
        try:
            ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
            return ingrediente.es_vegetariano and ingrediente.calorias < 100
        except Exception as e:
            print(f"Error al consultar si el ingrediente es sano: {e}")
            raise

# Reabastecer un producto según su ID
    def reabastecer_producto(self, producto_id, cantidad):
        """
        Reabastece un producto según su ID incrementando los inventarios de sus ingredientes.
        """
        try:
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0.")
            
            producto = Producto.query.get_or_404(producto_id)
            producto.ingrediente1.inventario += cantidad
            producto.ingrediente2.inventario += cantidad
            producto.ingrediente3.inventario += cantidad
            db.session.commit()
            return f"Producto '{producto.nombre}' reabastecido en {cantidad} unidades por ingrediente."
        except Exception as e:
            print(f"Error al reabastecer el producto: {e}")
            raise
            
# Renovar el inventario de un producto según su 
    def renovar_inventario_producto(self, producto_id):
        """
        Renueva el inventario de los ingredientes de un producto según su ID.
        """
        try:
            producto = Producto.query.get_or_404(producto_id)
            producto.ingrediente1.inventario = 50
            producto.ingrediente2.inventario = 50
            producto.ingrediente3.inventario = 50
            db.session.commit()
            return f"Inventario de '{producto.nombre}' renovado."
        except Exception as e:
            print(f"Error al renovar el inventario del producto: {e}")
            raise
