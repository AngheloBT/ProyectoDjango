from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    rut = models.CharField(max_length=12, unique=True)

class Client(models.Model)
    id = models.IntegerField(primary_key=True)

class Departament(models.Model):
    id_departament = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class Section(models.Model):
    id_section = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    departament = models.ForeignKey(Departament, on_delete=models.CASCADE)

class Product(models.Model):
    id_product = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    unit_price = models.FloatField()
    section = models.ForeignKey(Section, ondelete=models.SET_NULL, null=True)

class Order(models.Model):
    id_order = models.IntegerField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    hora = models.TimeField()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_total = models.FloatField()