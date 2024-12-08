from flask import abort
from flask_login import current_user
from functools import wraps

def role_required(role):
    """Decorador para verificar roles de usuario."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)  # Prohibido para usuarios no autenticados
            
            # Verificar el rol
            if role == 'admin' and not current_user.es_admin:
                abort(403)  # Solo administradores
            elif role == 'empleado' and not (current_user.es_admin or current_user.es_empleado):
                abort(403)  # Empleados y administradores
            elif role == 'cliente' and not (current_user.es_admin or current_user.es_cliente):
                abort(403)  # Clientes y administradores
            return func(*args, **kwargs)
        return wrapper
    return decorator

def public_access(func):
    """Decorador para rutas accesibles por cualquiera."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
