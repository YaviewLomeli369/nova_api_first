# Generated by Django 5.2.4 on 2025-07-23 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_comprobantefiscal_folio_comprobantefiscal_serie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comprobantefiscal',
            name='folio',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
