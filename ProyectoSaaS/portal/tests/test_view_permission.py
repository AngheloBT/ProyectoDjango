from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardAccessTest(TestCase):
    def setUp(self):
        self.user_credentials = {'username': 'testuser', 'password': '12345'}
        self.user = User.objects.create_user(**self.user_credentials)

    def test_login_required_for_dashboard(self):
        # intento de acceder sin logear
        resp = self.client.get(reverse('app'))
        self.assertEqual(resp.status_code, 302)  # redirige a login
