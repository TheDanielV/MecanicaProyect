from enum import Enum

from django.db import models
from django.utils import timezone


# Create your models here.

class AuthLog(models.Model):
    class EventType(Enum):
        LOGIN_SUCCESS = 'Inicio de sesión exitoso'
        LOGIN_FAILURE = 'Inicio de sesión fallido'
        PASSWORD_CHANGE = 'Cambio de contraseña'

    ip_address = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=100, choices=[(tag.name, tag.value) for tag in EventType],
                                  default=EventType.LOGIN_SUCCESS.name)

    @classmethod
    def create_log(cls, ip_address, event_type):
        """
        Método para crear un registro de autenticación.
        """
        log = AuthLog(ip_address=ip_address, event_type=event_type)
        log.save()
        return log

    class Meta:
        db_table = 'session_log'
