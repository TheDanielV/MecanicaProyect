from django.http import JsonResponse
from functools import wraps
from .models import Person  # Asegúrate de que Persona está correctamente importado


def role_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        username = request.session.get('username', 'default')
        if not username:
            return JsonResponse({'error': 'No username provided'}, status=400)

        try:
            persona = Person.objects.get(username=username)
        except Person.DoesNotExist:
            return JsonResponse({'error': 'Invalid username'}, status=401)

        # Si es necesario, puedes adjuntar el usuario al request
        request.persona = persona

        return view_func(request, *args, **kwargs)

    return _wrapped_view
