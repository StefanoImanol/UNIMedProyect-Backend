from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from api.models import Usuario

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            correo = data.get("email")  # Cambiamos a "correo"
            contraseña = data.get("password")  # Cambiamos a "contraseña"

            # Buscar el usuario en la base de datos
            user = Usuario.objects.filter(correo=correo).first()

            if user and user.check_password(contraseña):
                # Determinar tipo de usuario y redirigir
                if user.rol == "Administrador":
                    return JsonResponse({"redirect": "home-administrador"})
                elif user.rol == "Paciente":
                    return JsonResponse({"redirect": "home-paciente"})
                elif user.rol == "Medico":
                    return JsonResponse({"redirect": "home-medico"})
                else:
                    return JsonResponse({"error": "Rol de usuario no reconocido"}, status=400)
            else:
                return JsonResponse({"error": "Credenciales incorrectas"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos mal formateados."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error procesando solicitud: {str(e)}"}, status=500)

    elif request.method == "GET":
        return JsonResponse({"error": "Por favor, usa POST para enviar los datos"}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


