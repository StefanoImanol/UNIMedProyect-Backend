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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('', lambda request: redirect('/login/')),  # Asegúrate de que redirige a /login/
    path('register/', register_view, name='register'),
    path('api/profile-data/', profile_data_view, name='profile_data'),
    path('api/update-profile/', update_profile_view, name='update_profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]