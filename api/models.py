from django.db import models

class Usuario(models.Model):
    usuario_id = models.CharField(max_length=16, primary_key=True)
    nombre = models.CharField(max_length=64)
    correo = models.EmailField(max_length=64)
    contraseña = models.CharField(max_length=16)
    rol = models.CharField(max_length=16)  # Puede ser 'Paciente', 'Administrador', 'Medico'

    def __str__(self):
        return self.nombre


class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=32, primary_key=True)
    horario = models.CharField(max_length=128)

    def __str__(self):
        return self.nombre_especialidad


class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    horario = models.CharField(max_length=128)
    nombre_especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.nombre_especialidad}"


class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.usuario.nombre


class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    fecha_nacimiento = models.DateTimeField()
    codigo_uni = models.CharField(max_length=9)

    def __str__(self):
        return self.usuario.nombre


class Cita(models.Model):
    cita_id = models.CharField(max_length=16, primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=16)  # Estados posibles: 'Agendada', 'Cancelada', 'Completada'
    usuario_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    usuario_medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cita {self.cita_id} - {self.usuario_paciente.usuario.nombre} con {self.usuario_medico.usuario.nombre}"


class Notificacion(models.Model):
    notificacion_id = models.CharField(max_length=8, primary_key=True)
    mensaje = models.CharField(max_length=256)
    fecha_envio = models.DateTimeField()
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notificación {self.notificacion_id} para cita {self.cita.cita_id}"
