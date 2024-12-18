from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, contraseña=None, nombre=None, **extra_fields):
        if not correo:
            raise ValueError("El correo electrónico es obligatorio")
        
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)

        usuario = self.model(
            correo=self.normalize_email(correo),
            nombre=nombre,
            **extra_fields
        )
        if contraseña:
            usuario.set_password(contraseña)  # Asegúrate de cifrar las contraseñas
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, contraseña=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(correo, contraseña, **extra_fields)


class Usuario(AbstractBaseUser):
    ROLES = [
        ('Paciente', 'Paciente'),
        ('Medico', 'Medico'),
        ('Administrador', 'Administrador'),
    ]
    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64, null=True, blank=True)
    correo = models.EmailField(max_length=64, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='Paciente')  # Campo ROL
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'correo'  # Esto asegura que 'correo' sea el campo de autenticación
    REQUIRED_FIELDS = ['nombre', 'apellidos']

    objects = UsuarioManager()

    def __str__(self):
        return self.correo


class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    fecha_nacimiento = models.DateField()
    codigo_uni = models.CharField(max_length=9, unique=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    contacto_emergencia = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellidos} - {self.codigo_uni}"


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

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser menor que la hora de fin.")

# Modelo de Médico
class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='medicos')  # Cambiado aquí
    horarios = models.ManyToManyField(Horario)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.especialidad.nombre_especialidad}"


# Modelo de Administrador
class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.usuario.nombre

# Modelo de Paciente

# Modelo de Cita
class Cita(models.Model):
    cita_id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.BooleanField(default=False)  # Cambiado a BooleanField con valor predeterminado False
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
    enviada = models.BooleanField(default=False)  # Indica si la notificación fue enviada

    def __str__(self):
        return f"Notificación {self.notificacion_id} para cita {self.cita.cita_id}"
