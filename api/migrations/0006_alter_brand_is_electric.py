# Generated by Django 3.2.10 on 2024-06-28 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_accessoryimages_accessoryproducts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='is_electric',
            field=models.BooleanField(),
        ),
    ]
