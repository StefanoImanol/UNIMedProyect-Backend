# Generated by Django 5.1.3 on 2024-11-25 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='contraseña',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='correo',
            field=models.EmailField(max_length=64, unique=True),
        ),
    ]
