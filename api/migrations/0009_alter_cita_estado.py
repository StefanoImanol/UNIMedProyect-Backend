# Generated by Django 5.1.3 on 2024-12-06 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_usuario_rol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.BooleanField(default=False),
        ),
    ]
