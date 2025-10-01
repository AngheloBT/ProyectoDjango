from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class TestUserModel(TestCase):
    def test_create_user_with_rut(self):
        u = User.objects.create_user(username='testuser', password='pass', rut='12345678-9') #nosec B106
        self.assertEqual(u.rut, '12345678-9')
        self.assertTrue(u.check_password('pass'))
