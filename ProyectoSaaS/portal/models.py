from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    rut = models.CharField(max_length=12, unique=True)

class Client(models.Model):
    id_client = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)

class Departament(models.Model):
    id_departament = models.IntegerField(unique=True)

class Section(models.Model):
    id_section = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    departament = models.ForeignKey(Departament, on_delete=models.CASCADE)

class Product(models.Model):
    id_product = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    unit_price = models.FloatField()
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)

class Order(models.Model):
    id_order = models.IntegerField(unique=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    hora = models.TimeField()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_total = models.FloatField()