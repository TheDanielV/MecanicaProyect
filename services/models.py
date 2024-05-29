from django.db import models


class AuthUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'AuthUser'
