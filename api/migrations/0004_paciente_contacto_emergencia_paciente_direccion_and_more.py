# Generated by Django 5.1.3 on 2024-11-27 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_paciente_codigo_uni_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='contacto_emergencia',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='paciente',
            name='direccion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='paciente',
            name='telefono',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
