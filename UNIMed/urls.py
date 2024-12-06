"""
URL configuration for UNIMed project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect  # Cambiar la importación de redirect
from api.views import login_view, obtener_proxima_cita
from api.views import register_view
from api.views import profile_data_view, update_profile_view

from api.views import obtener_especialidades, obtener_medicos_por_especialidad, obtener_horarios_disponibles, crear_cita
from api.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from api.views import DatosPacienteView
from api.views import cancelar_cita
from api.views import reprogramar_cita
from api.views import obtener_agenda_medico
from api.views import get_medico_profile_data, update_medico_profile, update_medico_profile_image
from api.views import obtener_todas_citas, cambiar_estado_cita
from api.views import obtener_especialidad, crear_especialidad, eliminar_especialidad
from api.views import obtener_medicos_especialidades, crear_medico, editar_medico, eliminar_medico

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('', lambda request: redirect('/login/')),  # Asegúrate de que redirige a /login/
    path('register/', register_view, name='register'),
    path('api/profile-data/', profile_data_view, name='profile_data'),
    path('api/update-profile/', update_profile_view, name='update_profile'),
    path('datos-paciente/', DatosPacienteView.as_view(), name='datos_paciente'),
    path('especialidades/', obtener_especialidades, name='obtener_especialidades'),
    path('medicos/<int:especialidad_id>/', obtener_medicos_por_especialidad, name='obtener_medicos_por_especialidad'),
    path('horarios/<int:medico_id>/<str:fecha>/', obtener_horarios_disponibles, name='obtener_horarios_disponibles'),
    path('citas/', crear_cita, name='crear_cita'),
    path('api/proxima-cita/', obtener_proxima_cita, name='obtener_proxima_cita'),
    path('api/cancelar-cita/<int:cita_id>/', cancelar_cita, name='cancelar_cita'),
    path('api/reprogramar-cita/<int:cita_id>/', reprogramar_cita, name='reprogramar_cita'),
    path('api/agenda-medico/', obtener_agenda_medico, name='agenda_medico'),
    path('api/medico-profile-data/', get_medico_profile_data, name='get_medico_profile_data'),
    path('api/update-medico-profile/', update_medico_profile, name='update_medico_profile'),
    path('api/update-medico-image/', update_medico_profile_image, name='update_medico_profile_image'),
    path('api/todas-citas/', obtener_todas_citas, name='obtener_todas_citas'),
    path('api/cambiar-estado-cita/<int:cita_id>/', cambiar_estado_cita, name='cambiar_estado_cita'),
    path('api/especialidades/', obtener_especialidad, name='obtener_especialidad'),
    path('api/especialidades/crear/', crear_especialidad, name='crear_especialidad'),
    path('api/especialidades/eliminar/<int:especialidad_id>/', eliminar_especialidad, name='eliminar_especialidad'),
    path('api/medicos/<int:especialidad_id>/', obtener_medicos_especialidades, name='obtener_medicos_especialidad'),
    path('api/medicos/crear/', crear_medico, name='crear_medico'),
    path('api/medicos/editar/<int:medico_id>/', editar_medico, name='editar_medico'),
    path('api/medicos/eliminar/<int:medico_id>/', eliminar_medico, name='eliminar_medico'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]