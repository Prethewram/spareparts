# Generated by Django 3.2.10 on 2024-08-08 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20240808_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='main_vehicle',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='api.vehicle'),
        ),
    ]
