from django.contrib import admin
from .models import Usuario, Especialidad, Medico, Administrador, Paciente, Cita, Notificacion, Horario

# Registra los modelos
admin.site.register(Usuario)
admin.site.register(Horario)
admin.site.register(Especialidad)
admin.site.register(Medico)
admin.site.register(Administrador)
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(Notificacion)

