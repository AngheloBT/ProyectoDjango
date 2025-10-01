ProyectoSaaS

Descripción
ProyectoSaaS es una aplicación web desarrollada en Django que permite gestionar dashboards, usuarios y permisos de forma local. Incluye pruebas automatizadas con pytest y Selenium, y cuenta con la base de datos ya cargada para facilitar la instalación y ejecución inmediata.

Instalación

1. Crear y activar un entorno virtual:

python -m venv env
env\Scripts\activate   # Windows

# o

source env/bin/activate  # Linux / macOS

2. Instalar dependencias:

pip install -r requirements.txt

Para ejecutar pruebas, se recomienda instalar también las dependencias de desarrollo:

pip install -r requirements-dev.txt

3. Configurar base de datos:
   El proyecto incluye la base de datos ya cargada, por lo que no es necesario ejecutar migrate. Solo asegúrate de que el archivo de la base de datos esté en la ruta correcta y que settings.py lo apunte correctamente.

Ejecución del proyecto

1. Levantar el servidor local:

python manage.py runserver

2. Abrir el navegador y acceder a:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Pruebas
El proyecto incluye pruebas automatizadas:

* Unitarias: verifican funciones de dashboards, modelos y permisos.
* Selenium: pruebas de login y logout.
* Seguridad: análisis con bandit y pip-audit.

Ejecutar todas las pruebas:

pytest -v
bandit -r portal/
pip-audit


Notas adicionales

* La base de datos ya cargada permite probar la aplicación sin necesidad de migraciones ni creación de usuarios manual.
* El archivo requirements-dev.txt incluye todas las dependencias necesarias para ejecutar pruebas y análisis de seguridad.

Cuenta admin
username = anghelo
password = 123