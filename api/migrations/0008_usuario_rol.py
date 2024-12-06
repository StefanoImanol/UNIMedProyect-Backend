# Generated by Django 5.1.3 on 2024-12-06 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_medico_especialidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.CharField(choices=[('Paciente', 'Paciente'), ('Medico', 'Medico'), ('Administrador', 'Administrador')], default='Paciente', max_length=20),
        ),
    ]