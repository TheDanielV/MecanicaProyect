
from django.db import models
import hashlib



class AuthUser(models.Model):
    SALT = b'R\x12\xa3\x9a\xc3\x1eA\x1f[\xe56)\x84\x80\xec\x10'
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
        n = 2 ** 14
        r = 8
        p = 1
        maxmem = 0
        dklen = 64
        hashed_password = hashlib.scrypt(password.encode(), salt=cls.SALT, n=n, r=r, p=p, maxmem=maxmem, dklen=dklen)
        print()
        return hashed_password.hex()

    class Meta:
        db_table = 'auth_user'


