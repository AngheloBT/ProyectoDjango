from portal.models import Client, Departament, Section, Product, Order, OrderItem
from portal.cleaning.data_cleaner import clean_data

def insertar_datos(raw_data):
    df_limpio = clean_data(raw_data)

    for _, row in df_limpio.iterrows():
        row = row.to_dict()

        # Cliente
        cliente, _ = Client.objects.get_or_create(
            id_client=row["id_cliente"],
            defaults={"nombre": row.get("nombre_cliente", None)}
        )

        # Departamento
        departament, _ = Departament.objects.get_or_create(
            id_departament=row["id_departamento"],
        )

        # Sección
        section, _ = Section.objects.get_or_create(
            id_section=row["id_seccion"],
            defaults={
                "name": row["seccion_nombre"],
                "departament": departament
            }
        )

        # Producto
        product, _ = Product.objects.get_or_create(
            id_product=row["id_producto"],
            defaults={
                "name": row["nombre_producto"],
                "unit_price": row["precio_unitario"],
                "section": section
            }
        )

        # Pedido
        order, _ = Order.objects.get_or_create(
            id_order=row["id_pedido"],
            defaults={
                "client": cliente,
                "fecha": row["fecha"],
                "hora": row["hora"]
            }
        )

        # Detalle del pedido
        OrderItem.objects.create(
            order=order,
            product=product,
            cantidad=row["cantidad"],
            precio_total=row["precio_total"]
        )
