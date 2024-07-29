import re
import uuid
import secrets
from datetime import timedelta

from django.db import models
import hashlib
from django.db import IntegrityError
from .utils import send_token_email
from django.utils import timezone


class AuthUser(models.Model):
    SALT = b'R\x12\xa3\x9a\xc3\x1eA\x1f[\xe56)\x84\x80\xec\x10'
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, unique=True, null=False, default="00000")

    def create_user(self, username, password, email):
        if not self.is_a_valid_password(password):
            raise InvalidPassword("patron incorrecto ")
        else:
            self.username = username
            self.password = self.hashed_password(password)
            self.email = email
            self.token = str(uuid.uuid4())
            return self.token

    @classmethod
    def update_password(cls, token, password):
        try:
            user = cls.objects.get(token=token)
            if cls.is_a_valid_password(password):
                user.password = cls.hashed_password(password)
                user.save()
                return True
            else:
                raise ValueError("Contraseña inválida")
        except cls.DoesNotExist:
            raise ValueError("Usuario con el token proporcionado no existe")
        except Exception as e:
            raise e

    @classmethod
    def is_authorized(cls, username, password):
        try:

            auth_user = cls.objects.using('auth_db').get(username=username)
            if auth_user.username == username and auth_user.password == cls.hashed_password(password):
                return auth_user.token
        except cls.DoesNotExist:
            return None

    @classmethod
    def hashed_password(cls, password):
        """
        Genera un hash seguro de la contraseña utilizando el algoritmo scrypt.

        Args:
            password (str): La contraseña en texto plano que se desea hashear.

        Returns:
            str: La contraseña hasheada en formato hexadecimal.

        """

        n = 2 ** 14
        r = 8
        p = 1
        maxmem = 0
        dklen = 64
        hashed_password = hashlib.scrypt(password.encode(), salt=cls.SALT, n=n, r=r, p=p, maxmem=maxmem, dklen=dklen)
        print()
        return hashed_password.hex()

    @classmethod
    def is_a_valid_password(cls, password):
        pattern = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).{8,}$'
        if re.fullmatch(pattern, password):
            return True

    class Meta:
        db_table = 'auth_user'


class PasswordReset(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, unique=True, null=False, default="00000")
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_remember_password_token(cls, email):
        try:
            user = AuthUser.objects.get(email=email)
            password_reset = cls(email=email, token=secrets.token_urlsafe(5))
            if send_token_email(password_reset.email, password_reset.token):
                password_reset.save()
                return password_reset
            else:
                raise Exception("Fallo al enviar el correo")
        except AuthUser.DoesNotExist:
            raise Exception("El email no pertenece a un usuario")
        except IntegrityError:
            raise Exception("Error al generar el token")

    @classmethod
    def update_password_with_token(cls, token):
        try:
            if cls.is_the_token_expired(token):
                cls.objects.get(token=token).delete()
                raise Exception("El token expiró")
            else:
                password_reset = cls.objects.get(token=token)
                password_reset.delete()
                return AuthUser.objects.get(email=password_reset.email).token
        except PasswordReset.DoesNotExist:
            raise Exception("Token no válido o ya usado")
        except AuthUser.DoesNotExist:
            raise Exception("Usuario no encontrado")
        except PasswordReset.DoesNotExist:
            raise Exception("Token incorrecto o inválido")

    @classmethod
    def is_the_token_expired(cls, token):
        try:
            password_remember = cls.objects.get(token=token)
            if timezone.now() > password_remember.created_at + timedelta(minutes=5):
                return True
            else:
                return False
        except cls.DoesNotExist:
            return True


class InvalidPassword(Exception):
    def __int__(self, message):
        self.message = message
        super().__int__(f"{message}:")
