from functools import wraps

from django.http import HttpResponseForbidden


def key_user_required(value):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Comprueba el valor de la variable global
            if value is not None:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator
