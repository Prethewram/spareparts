# Generated by Django 3.2.10 on 2024-06-25 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_brand_is_electric'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='version_fuel_type',
            field=models.CharField(max_length=100, null=True),
        ),
    ]