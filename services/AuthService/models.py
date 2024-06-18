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

    def update_password(self, token, password):
        auth_user = self.objects.get(token=token)
        if self.is_a_valid_password(password):
            auth_user.password = self.hashed_password(password)
            self.save()
        else:
            return Exception("Contraseña inválida")

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

    def get_remember_password_token(self, email):
        password_reset = PasswordReset()
        if AuthUser.objects.get(email=email) is not None:
            self.email = email
            self.token = secrets.token_urlsafe(5)
        else:
            return Exception("El email no pertenece a un usuario")
        try:
            if send_token_email(self.email, self.token):
                self.save()
            else:
                return Exception("Fallo al enviar el correo")
            # TODO: Logs para almacenar el cambio de contraseña
        except IntegrityError as e:
            return Exception("Error al generar el token")

    def update_password_with_token(self, token):
        if self.is_the_token_expired(token):
            token = PasswordReset.objects.get(token=token)
            token.delete()
            return Exception("el token expiró")
        else:
            passwordReset = PasswordReset.objects.get(token=token)
            return AuthUser.objects.get(email=passwordReset.email).token

    def is_the_token_expired(self, token):
        passwordRemember = self.objects.get(token=token)
        if timezone.now() > passwordRemember.created_at + timedelta(minutes=5):
            return True
        else:
            return False


class InvalidPassword(Exception):
    def __int__(self, message):
        self.message = message
        super().__int__(f"{message}:")
