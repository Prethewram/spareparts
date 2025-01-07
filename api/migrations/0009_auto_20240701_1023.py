# Generated by Django 3.2.10 on 2024-07-01 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_category_vehicle_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='description',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='electric',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
