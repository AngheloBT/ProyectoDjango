from django.test import TestCase
from portal.models import Departament, Section, Product, Order, OrderItem, Client
from portal.dashboards.plotly_dashboards import lift_confianza_data, dashboard_lift_confianza
import pandas as pd
from datetime import date, datetime

class TestDashboardFunction(TestCase):
    def setUp(self):
        client = Client.objects.create(id_client=1, nombre='Cliente 1')
        dep = Departament.objects.create(id_departament=1)
        sec = Section.objects.create(id_section=1, name='Sección 1', departament=dep)
        
        # Crear 2 productos diferentes
        prod1 = Product.objects.create(id_product=1, name='Producto 1', unit_price=100, section=sec)
        prod2 = Product.objects.create(id_product=2, name='Producto 2', unit_price=150, section=sec)
        
        order = Order.objects.create(id_order=1, client=client, fecha=date.today(), hora=datetime.now().time())
        
        # Agregar ambos productos al mismo pedido
        OrderItem.objects.create(order=order, product=prod1, cantidad=1, precio_total=100)
        OrderItem.objects.create(order=order, product=prod2, cantidad=1, precio_total=150)


    def test_lift_confianza_data_not_empty(self):
        df = lift_confianza_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty) 

    def test_dashboard_lift_confianza_basic_structure(self):
        result = dashboard_lift_confianza()
        self.assertIsInstance(result, str)
        self.assertIn('<div', result)

