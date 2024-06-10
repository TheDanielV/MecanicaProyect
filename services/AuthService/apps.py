from django.apps import AppConfig

from services import AuthService


class AuthserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services.AuthService'
