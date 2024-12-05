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
from api.views import login_view
from api.views import register_view
from api.views import profile_data_view, update_profile_view

from api.views import obtener_especialidades, obtener_medicos_por_especialidad, obtener_horarios_disponibles, crear_cita
from api.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from api.views import DatosPacienteView
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
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]