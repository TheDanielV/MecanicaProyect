from functools import wraps
from django.http import JsonResponse
from .models import Customer, Admin

def role_login_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.session.get('token')
            if not token:
                return JsonResponse({'error': 'No username provided'}, status=400)

            persona = None
            try:
                # Primero intentar obtener como Customer
                persona = Customer.objects.get(token=token)
                request.session['role'] = persona.role
                request.session['full_name'] = persona.name + ' ' + persona.last_name
            except Customer.DoesNotExist:
                try:
                    # Si no existe como Customer, intentar como Admin
                    persona = Admin.objects.get(token=token)
                except Admin.DoesNotExist:
                    return JsonResponse({'error': 'Invalid username'}, status=401)

            if allowed_roles and persona.role not in allowed_roles:
                return JsonResponse({'error': 'Unauthorized'}, status=403)

            request.persona = persona
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
