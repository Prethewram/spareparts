# Generated by Django 3.2.10 on 2024-07-05 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_product_product_offer_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_offer_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]