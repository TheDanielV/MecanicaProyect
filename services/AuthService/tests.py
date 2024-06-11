from django.test import TestCase
from services.AuthService.models import AuthUser,InvalidPassword


# Create your tests here.
class AuthUserTestCase(TestCase):

    def test_invalid_password_on_create(self):
        test_instance = AuthUser()
        with self.assertRaises(InvalidPassword):
            test_instance.create_user("Daniel", "1234", "test@email.com")
