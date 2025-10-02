from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator that restricts access to a route to users with specific roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # This should be handled by login_required, but as a safeguard
                abort(401)
            if current_user.role.value not in roles:
                # If the user does not have any of the required roles
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator