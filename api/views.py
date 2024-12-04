from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from api.models import Usuario
from api.models import Paciente
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate, login

from django.contrib.auth import login
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            print(f"Headers recibidos: {request.headers}")  # Para comparar encabezados
            print(f"Cookies recibidas: {request.COOKIES}")  # Para verificar cookies
            print(f"Body recibido: {request.body}")  # Para verificar el cuerpo JSON

            data = json.loads(request.body)
            correo = data.get("email")
            contraseña = data.get("password")

            print(f"Correo recibido: {correo}")
            print(f"Contraseña recibida: {contraseña}")

            user = authenticate(request, username=correo, password=contraseña)
            if user is None:
                print("Autenticación fallida")
                return JsonResponse({"error": "Credenciales incorrectas"}, status=401)
            else:
                print(f"Usuario autenticado: {user}")
                login(request, user)
                return JsonResponse({"message": "Login exitoso", "redirect": "home-paciente"})
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return JsonResponse({"error": "Cuerpo de solicitud no es JSON válido"}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        try:
            # Parsear datos
            data = json.loads(request.body)

            # Validar que todos los campos necesarios estén presentes
            required_fields = ["nombre", "correo", "contrasena", "fecha_nacimiento", "codigo_uni"]
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({"error": f"El campo '{field}' es obligatorio."}, status=400)

            # Validar el dominio del correo
            correo = data.get("correo")
            if not correo.endswith("@uni.pe"):
                return JsonResponse({"error": "El correo debe tener dominio '@uni.pe'"}, status=400)

            # Validar que el correo sea único
            if Usuario.objects.filter(correo=correo).exists():
                return JsonResponse({"error": "El correo ya está registrado"}, status=400)

            # Validar que el código universitario sea único
            if Paciente.objects.filter(codigo_uni=data.get("codigo_uni")).exists():
                return JsonResponse({"error": "El código universitario ya está registrado"}, status=400)

            # Crear el usuario
            usuario = Usuario(
                nombre=data["nombre"],
                apellidos=data.get("apellidos"),
                correo=data["correo"],
            )
            usuario.set_password(data["contrasena"])
            usuario.save()

            # Crear el paciente vinculado al usuario
            paciente = Paciente(
                usuario=usuario,
                fecha_nacimiento=data["fecha_nacimiento"],
                codigo_uni=data["codigo_uni"],
            )
            paciente.save()

            return JsonResponse({"message": "Paciente registrado exitosamente"}, status=201)

        except IntegrityError as e:
            # Detectar duplicados en restricciones únicas
            if "unique constraint" in str(e):
                return JsonResponse({"error": "El correo o código ya está registrado"}, status=400)
            return JsonResponse({"error": "Error al procesar el registro"}, status=500)
        except Exception as e:
            # Log de errores
            print(f"Error en register_view: {str(e)}")
            return JsonResponse({"error": "Error interno en el servidor. Verifica los datos enviados."}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@csrf_exempt
def profile_data_view(request):
    print("Cookies recibidas en la solicitud:", request.COOKIES)
    print("Usuario autenticado:", request.user.is_authenticated)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    if request.method == 'GET':
        try:
            user = request.user
            paciente = Paciente.objects.get(usuario=user)
            response_data = {
                'nombre': user.nombre,
                'apellidos': user.apellidos,
                'correo': user.correo,
                'codigo': paciente.codigo_uni,
                'direccion': paciente.direccion,
                'telefono': paciente.telefono,
                'emergencia': paciente.contacto_emergencia,
                'profile_image': paciente.profile_image.url if hasattr(paciente, 'profile_image') else None,
            }
            return JsonResponse(response_data, status=200)
        except Paciente.DoesNotExist:
            return JsonResponse({'error': 'Paciente no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def update_profile_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
    
    if request.method == 'PUT':
        user = request.user
        data = request.POST
        files = request.FILES
        try:
            paciente = Paciente.objects.get(usuario=user)

            # Actualiza datos básicos
            user.nombre = data.get('nombre', user.nombre)
            user.apellidos = data.get('apellidos', user.apellidos)
            user.correo = data.get('correo', user.correo)
            user.save()

            # Actualiza datos específicos de Paciente
            paciente.direccion = data.get('direccion', paciente.direccion)
            paciente.telefono = data.get('telefono', paciente.telefono)
            paciente.contacto_emergencia = data.get('emergencia', paciente.contacto_emergencia)
            if 'profile_image' in files:
                paciente.profile_image = files['profile_image']
            paciente.save()

            return JsonResponse({'message': 'Perfil actualizado correctamente'}, status=200)
        except Paciente.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)
