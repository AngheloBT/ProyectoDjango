from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumLoginTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Edge()  # o Chrome si prefieres
        cls.driver.implicitly_wait(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def login_via_session(self):
        """Crea un usuario y establece la sesión en Selenium"""
        from django.contrib.auth import get_user_model
        from django.contrib.sessions.models import Session
        User = get_user_model()

        # Crear usuario si no existe
        if not User.objects.filter(username="testuser").exists():
            User.objects.create_user(username="testuser", password="123456")

        # Usar el cliente de Django para login y obtener la cookie de sesión
        from django.test import Client
        client = Client()
        client.login(username="testuser", password="123456")
        sessionid = client.cookies['sessionid'].value

        # Abrir la página inicial para poder setear cookies
        self.driver.get(self.live_server_url + "/")
        self.driver.add_cookie({'name': 'sessionid', 'value': sessionid, 'path': '/'})

        # Refrescar para que el usuario autenticado se renderice
        self.driver.refresh()

    def test_logout_redirect(self):
        # Loguear usuario vía sesión
        self.login_via_session()

        # Abrir el dropdown del usuario (esperar que aparezca)
        dropdown_toggle = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "navbarDropdown"))
        )
        dropdown_toggle.click()

        # Hacer click en logout (esperar que aparezca)
        logout_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/logout/']/button"))
        )
        logout_button.click()

        # Verificar que redirige al login
        WebDriverWait(self.driver, 5).until(
            EC.url_contains(reverse('login'))
        )
        self.assertIn(reverse('login'), self.driver.current_url)
