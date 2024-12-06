from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from api.models import Usuario
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'correo'  # Este indica que el campo de autenticación es 'correo'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añadir información personalizada al token si es necesario
        token['correo'] = user.correo
        token['rol'] = user.rol  # Añadir el rol al token
        return token

    def validate(self, attrs):
        correo = attrs.get('correo')
        password = attrs.get('password')

        try:
            user = Usuario.objects.get(correo=correo)
            if not user.check_password(password):
                raise serializers.ValidationError('Credenciales inválidas')
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Credenciales inválidas')

        if not user.is_active:
            raise serializers.ValidationError('Cuenta inactiva')

        # Generar tokens manualmente
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'rol': user.rol,  # Incluye el rol en la respuesta
        }

