# Generated by Django 3.2.10 on 2024-06-28 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_category_vehicle_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='vehicle_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.maincategory'),
        ),
    ]