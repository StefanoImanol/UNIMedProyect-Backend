from django.db import models

# Modelo de Usuario
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64, null=True, blank=True)
    correo = models.EmailField(max_length=64, unique=True)
    contraseña = models.CharField(max_length=128)  # Contraseña encriptada
    ROL_CHOICES = [
        ('Paciente', 'Paciente'),
        ('Administrador', 'Administrador'),
        ('Medico', 'Medico'),
    ]
    rol = models.CharField(max_length=16, choices=ROL_CHOICES)

    def __str__(self):
        return self.correo

    def set_password(self, raw_password):
        """Encripta y guarda la contraseña."""
        self.contraseña = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica la contraseña encriptada."""
        return check_password(raw_password, self.contraseña)


# Modelo de Especialidad
class Especialidad(models.Model):
    especialidad_id = models.AutoField(primary_key=True)  # Clave primaria autoincremental
    nombre_especialidad = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.nombre_especialidad

# Modelo de Horario
class Horario(models.Model):
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE, related_name='horarios')
    DIAS_CHOICES = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    dia = models.CharField(max_length=16, choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.especialidad.nombre_especialidad} - {self.dia}: {self.hora_inicio} - {self.hora_fin}"

# Modelo de Médico
class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    horarios = models.ManyToManyField(Horario)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.especialidad.nombre_especialidad}"

# Modelo de Administrador
class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.usuario.nombre

# Modelo de Paciente
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    fecha_nacimiento = models.DateTimeField()
    codigo_uni = models.CharField(max_length=9)

    def __str__(self):
        return self.usuario.nombre

# Modelo de Cita
class Cita(models.Model):
    cita_id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=16)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cita {self.cita_id} - {self.paciente.usuario.nombre} con {self.medico.usuario.nombre}"

# Modelo de Notificación
class Notificacion(models.Model):
    notificacion_id = models.AutoField(primary_key=True)
    mensaje = models.CharField(max_length=256)
    fecha_envio = models.DateTimeField()
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notificación {self.notificacion_id} para cita {self.cita.cita_id}"
