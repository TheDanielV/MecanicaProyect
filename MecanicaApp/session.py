from django.db import models


class Session(models.Model):
    session_key = models.CharField(max_length=30)
    user = models.CharField(max_length=30)
    type = models.CharField(max_length=30)

    class Meta:
        db_table = 'session'
