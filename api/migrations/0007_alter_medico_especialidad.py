# Generated by Django 5.1.3 on 2024-12-05 06:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_usuario_rol_notificacion_enviada_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medico',
            name='especialidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicos', to='api.especialidad'),
        ),
    ]
