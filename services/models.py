from django.db import models
import hashlib


class AuthUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)

    def create_user(self, username, password, email):
        self.username = username
        self.password = self.hashed_password(password)
        self.email = email

    @classmethod
    def is_authorized(cls, username, password):
        try:
            auth_user = cls.objects.using('auth_db').get(username=username)
            if auth_user.username == username & auth_user.password == cls.hashed_password(password):
                return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def hashed_password(cls, password):
        return hashlib.sha256(password.encode()).hexdigest()

    class Meta:
        db_table = 'AuthUser'
