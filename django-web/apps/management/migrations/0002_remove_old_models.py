# Generated manually to remove old models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        # Remove all old tables
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_reporte CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_costo CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_controlcalidad CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_procesoproduccion CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_lote CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_producto CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS management_proveedor CASCADE;",
            reverse_sql="-- Cannot reverse this operation"
        ),
    ]
