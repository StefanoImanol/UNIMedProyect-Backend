from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from api.models import Usuario
from api.models import Paciente
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate, login

from django.contrib.auth import login

from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Paciente
from django.shortcuts import get_object_or_404
from api.models import Medico, Horario, Cita
from django.utils.dateparse import parse_date
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("CustomTokenObtainPairView ejecutado")
        return super().post(request, *args, **kwargs)
      
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken

def generar_tokens_para_usuario(usuario):
    try:
        refresh = RefreshToken.for_user(usuario)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    except Exception as e:
        print(f"Error al generar tokens: {e}")  # Log adicional
        raise e

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user = Usuario.objects.filter(correo=username).first()
            if user and user.check_password(password):
                tokens = generar_tokens_para_usuario(user)
                return JsonResponse({"tokens": tokens, "message": "Autenticación exitosa"})
            else:
                # Usuario no encontrado o contraseña incorrecta
                return JsonResponse({"error": "Credenciales incorrectas"}, status=401)
        except Exception as e:
            return JsonResponse({"error": f"Error procesando solicitud: {str(e)}"}, status=500)
    return JsonResponse({"error": "Por favor, usa POST para enviar los datos"}, status=405)

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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Paciente

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_data_view(request):
    user = request.user
    try:
        paciente = get_object_or_404(Paciente, usuario=user)
        response_data = {
            'nombre': user.nombre,
            'apellidos': user.apellidos,
            'correo': user.correo,
            'rol': user.rol,  # Incluye el rol aquí
            'codigo': paciente.codigo_uni,
            'direccion': paciente.direccion,
            'telefono': paciente.telefono,
            'emergencia': paciente.contacto_emergencia,
            'profile_image': paciente.profile_image.url if hasattr(paciente, 'profile_image') else None,
        }
        return Response(response_data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user = request.user
    data = request.data
    try:
        paciente = get_object_or_404(Paciente, usuario=user)

        # Actualiza datos básicos
        user.nombre = data.get('nombre', user.nombre)
        user.apellidos = data.get('apellidos', user.apellidos)
        user.correo = data.get('correo', user.correo)
        user.save()

        # Actualiza datos específicos de Paciente
        paciente.direccion = data.get('direccion', paciente.direccion)
        paciente.telefono = data.get('telefono', paciente.telefono)
        paciente.contacto_emergencia = data.get('emergencia', paciente.contacto_emergencia)
        if 'profile_image' in request.FILES:
            paciente.profile_image = request.FILES['profile_image']
        paciente.save()

        return Response({'message': 'Perfil actualizado correctamente'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from api.models import Especialidad, Medico, Horario, Cita
from django.utils.dateparse import parse_time, parse_date
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import Paciente

class DatosPacienteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Usuario autenticado
        try:
            # Aquí usamos 'usuario' como se define en el modelo
            paciente = Paciente.objects.get(usuario=user)
            data = {
                "nombre": paciente.usuario.nombre,  # Accede al nombre del usuario relacionado
                "apellidos": paciente.usuario.apellidos,  # Accede a los apellidos
                "fecha_nacimiento": paciente.fecha_nacimiento,
                "codigo_uni": paciente.codigo_uni,
                "direccion": paciente.direccion,
                "telefono": paciente.telefono,
                "contacto_emergencia": paciente.contacto_emergencia,
            }
            return JsonResponse(data)
        except Paciente.DoesNotExist:
            return JsonResponse({"error": "Paciente no encontrado"}, status=404)

# Obtener todas las especialidades
def obtener_especialidades(request):
    especialidades = Especialidad.objects.all().values('especialidad_id', 'nombre_especialidad')
    return JsonResponse(list(especialidades), safe=False)

# Obtener médicos por especialidad
def obtener_medicos_por_especialidad(request, especialidad_id):
    especialidad = get_object_or_404(Especialidad, pk=especialidad_id)
    medicos = especialidad.medicos.all().values('usuario__nombre', 'usuario__apellidos', 'usuario_id')
    return JsonResponse(list(medicos), safe=False)

# Obtener horarios disponibles
from datetime import timedelta

def obtener_horarios_disponibles(request, medico_id, fecha):
    try:
        medico = Medico.objects.get(pk=medico_id)
        fecha_obj = parse_date(fecha)

        horarios_disponibles = []
        for horario in medico.horarios.all():
            # Filtra las citas existentes
            citas = Cita.objects.filter(
                medico=medico,
                fecha=fecha_obj,
                hora__gte=horario.hora_inicio,
                hora__lt=horario.hora_fin
            )
            horas_ocupadas = [cita.hora for cita in citas]

            # Itera sobre las horas y agrega solo las disponibles
            hora_actual = horario.hora_inicio
            while hora_actual < horario.hora_fin:
                if hora_actual not in horas_ocupadas:
                    horarios_disponibles.append({
                        "hora": hora_actual.strftime('%H:%M'),
                        "disponible": True
                    })
                hora_actual = (datetime.combine(datetime.min, hora_actual) + timedelta(hours=1)).time()

        # Devuelve horarios únicos (sin duplicados)
        horarios_unicos = {h["hora"]: h for h in horarios_disponibles}.values()
        return JsonResponse(list(horarios_unicos), safe=False)
    except Medico.DoesNotExist:
        return JsonResponse({"error": "Médico no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_datos_paciente(request):
    try:
        # Usar el campo correcto para filtrar
        paciente = Paciente.objects.get(usuario=request.user)
        return JsonResponse({
            "nombre": paciente.usuario.nombre,
            "apellidos": paciente.usuario.apellidos,
            "codigo_uni": paciente.codigo_uni,
        })
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cita(request):
    try:
        data = request.data  # Usa `request.data` en lugar de `json.loads(request.body)`
        paciente = Paciente.objects.get(usuario=request.user)  # Obtén el paciente autenticado
        medico_id = data.get('medico_id')
        fecha = parse_date(data.get('fecha'))
        hora = parse_time(data.get('hora'))

        cita = Cita.objects.create(
            paciente=paciente,
            medico_id=medico_id,
            fecha=fecha,
            hora=hora,
            estado='pendiente'
        )
        return JsonResponse({"mensaje": "Cita creada exitosamente", "cita_id": cita.cita_id})
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error al crear cita: {str(e)}"}, status=400)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Cita
from django.utils.timezone import now


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_proxima_cita(request):
    try:
        usuario = request.user
        cita = Cita.objects.filter(paciente__usuario=usuario, fecha__gte=now()).order_by('fecha', 'hora').first()
        if not cita:
            return Response({'message': 'No se encontraron próximas citas'}, status=404)

        response_data = {
            'id': cita.cita_id,  # Incluye el ID aquí
            'dia': cita.fecha.strftime('%d/%m/%Y'),
            'hora': cita.hora.strftime('%I:%M %p'),
            'especialidad': cita.medico.especialidad.nombre_especialidad,
            'doctor': f"{cita.medico.usuario.nombre} {cita.medico.usuario.apellidos}",
            'medico_id': cita.medico.usuario.usuario_id  # ID del médico (usuario_id de api_usuario)
        }
        return Response(response_data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancelar_cita(request, cita_id):
    try:
        cita = get_object_or_404(Cita, pk=cita_id)
        cita.delete()  # Elimina la cita de la base de datos
        return Response({'message': 'Cita cancelada exitosamente'}, status=200)
    except Exception as e:
        return Response({'error': f'Error al cancelar la cita: {str(e)}'}, status=400)
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Cita

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reprogramar_cita(request, cita_id):
    try:
        cita = get_object_or_404(Cita, pk=cita_id)
        nueva_fecha = request.data.get('fecha')
        nueva_hora = request.data.get('hora')

        if not nueva_fecha or not nueva_hora:
            return Response({'error': 'Faltan datos para la reprogramación.'}, status=400)

        cita.fecha = nueva_fecha
        cita.hora = nueva_hora
        cita.save()

        return Response({'message': 'Cita reprogramada exitosamente.'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Cita
from django.utils.timezone import now

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_agenda_medico(request):
    try:
        usuario = request.user
        medico = Medico.objects.get(usuario=usuario)
        citas = Cita.objects.filter(medico=medico, fecha__gte=now()).order_by('fecha', 'hora')

        data = []
        for cita in citas:
            paciente = cita.paciente.usuario  # Relación con el modelo Usuario
            data.append({
                # Ya no se envía 'foto'
                'nombre': f"{paciente.nombre} {paciente.apellidos}",
                'fechaConsulta': cita.fecha.strftime('%Y-%m-%d'),
                'horaConsulta': cita.hora.strftime('%H:%M:%S'),
            })

        return Response(data, status=200)
    except Medico.DoesNotExist:
        return Response({'error': 'El usuario no es un médico'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Usuario
from django.contrib.auth.decorators import login_required
from django.db import transaction


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_medico_profile_data(request):
    try:
        user = request.user
        data = {
            "nombre": user.nombre,
            "apellidos": user.apellidos,
            "correo": user.correo
        }
        return Response(data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_medico_profile(request):
    try:
        user = request.user
        user_data = request.data

        # Actualizar los campos enviados en la solicitud
        user.nombre = user_data.get('nombre', user.nombre)
        user.apellidos = user_data.get('apellidos', user.apellidos)
        user.save()

        return Response({"message": "Perfil actualizado correctamente."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_medico_profile_image(request):
    try:
        user = request.user
        profile_image = request.FILES.get('profile_image')

        if profile_image:
            user.profile_image = profile_image
            user.save()

        return Response({"message": "Imagen actualizada correctamente."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Cita
from django.utils.timezone import now

from django.db.models import F

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_todas_citas(request):
    try:
        citas = Cita.objects.all().order_by('-fecha', '-hora')  # Ordenar por fecha y hora ascendente
        data = [
            {
                'id': cita.cita_id,
                'doctor': f"{cita.medico.usuario.nombre} {cita.medico.usuario.apellidos}",
                'paciente': f"{cita.paciente.usuario.nombre} {cita.paciente.usuario.apellidos}",
                'fecha': cita.fecha.strftime('%d/%m/%Y'),
                'hora': cita.hora.strftime('%I:%M %p'),
                'estado': cita.estado,
            }
            for cita in citas
        ]
        return Response(data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH'])
def cambiar_estado_cita(request, cita_id):
    try:
        cita = Cita.objects.get(cita_id=cita_id)
        nuevo_estado = request.data.get('estado')

        if nuevo_estado is not None:
            cita.estado = nuevo_estado  # True o False desde el frontend
            cita.save()

        return Response({'message': 'Estado de la cita actualizado correctamente.'})
    except Cita.DoesNotExist:
        return Response({'error': 'La cita no existe.'}, status=404)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.models import Especialidad

from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Especialidad


@api_view(['GET'])
def obtener_especialidad(request):
    especialidades = Especialidad.objects.all()
    especialidades_data = [
        {'especialidad_id': e.especialidad_id, 'nombre_especialidad': e.nombre_especialidad}
        for e in especialidades
    ]
    return Response(especialidades_data)


@api_view(['POST'])
def crear_especialidad(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({'error': 'El nombre de la especialidad es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
    if Especialidad.objects.filter(nombre_especialidad=nombre).exists():
        return Response({'error': 'La especialidad ya existe.'}, status=status.HTTP_400_BAD_REQUEST)
    especialidad = Especialidad.objects.create(nombre_especialidad=nombre)
    return Response({'message': 'Especialidad creada exitosamente.', 'id': especialidad.especialidad_id}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def eliminar_especialidad(request, especialidad_id):
    try:
        especialidad = Especialidad.objects.get(especialidad_id=especialidad_id)
        especialidad.delete()
        return Response({'message': 'Especialidad eliminada exitosamente.'}, status=status.HTTP_200_OK)
    except Especialidad.DoesNotExist:
        return Response({'error': 'Especialidad no encontrada.'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Medico, Horario, Especialidad, Usuario
from django.db import transaction
@api_view(['POST'])
def crear_medico(request):
    try:
        with transaction.atomic():
            # Crear el usuario
            usuario = Usuario.objects.create_user(
                correo=request.data["correo"],
                contraseña=request.data["contrasena"],
                nombre=request.data["nombre"],
                rol='Medico'
            )

            # Crear el médico
            especialidad = Especialidad.objects.get(especialidad_id=request.data["especialidad_id"])
            medico = Medico.objects.create(usuario=usuario, especialidad=especialidad)

            # Crear horarios y asociarlos al médico
            for horario in request.data["horarios"]:
                nuevo_horario = Horario.objects.create(
                    especialidad=especialidad,
                    dia=horario["dia"],
                    hora_inicio=horario["hora_inicio"],
                    hora_fin=horario["hora_fin"]
                )
                medico.horarios.add(nuevo_horario)

        return Response({"message": "Médico creado exitosamente."}, status=status.HTTP_201_CREATED)

    except Especialidad.DoesNotExist:
        return Response({"error": "Especialidad no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_medico(request, medico_id):
    try:
        medico = Medico.objects.get(pk=medico_id)
        usuario = medico.usuario

        # Actualizar datos del usuario
        usuario.nombre = request.data.get("nombre", usuario.nombre)
        usuario.correo = request.data.get("correo", usuario.correo)
        usuario.save()

        # Actualizar horarios: Eliminar los existentes y agregar nuevos
        medico.horarios.clear()
        for horario in request.data.get("horarios", []):
            nuevo_horario = Horario.objects.create(
                especialidad=medico.especialidad,
                dia=horario["dia"],
                hora_inicio=horario["hora_inicio"],
                hora_fin=horario["hora_fin"]
            )
            medico.horarios.add(nuevo_horario)

        return Response({"message": "Médico actualizado correctamente."}, status=status.HTTP_200_OK)

    except Medico.DoesNotExist:
        return Response({"error": "Médico no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def eliminar_medico(request, medico_id):
    print(f"ID recibido en la solicitud: {medico_id}")
    try:
        medico = Medico.objects.get(pk=medico_id)  # Verifica que el médico existe
        print(f"Médico encontrado: {medico}")
        medico.delete()
        return Response({"message": "Médico eliminado correctamente."}, status=status.HTTP_200_OK)
    except Medico.DoesNotExist:
        print(f"No se encontró un médico con ID: {medico_id}")
        return Response({"error": "Médico no encontrado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def obtener_medicos_especialidades(request, especialidad_id):
    try:
        medicos = Medico.objects.filter(especialidad_id=especialidad_id).select_related('usuario').prefetch_related('horarios')
        medicos_data = [
            {
                'id': medico.usuario.usuario_id,
                'usuario__nombre': medico.usuario.nombre,
                'usuario__apellidos': medico.usuario.apellidos,
                'horarios': [
                    {
                        'dia': horario.dia,
                        'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                        'hora_fin': horario.hora_fin.strftime('%H:%M')
                    } for horario in medico.horarios.all()
                ]
            } for medico in medicos
        ]
        return Response(medicos_data, status=status.HTTP_200_OK)
    except Especialidad.DoesNotExist:
        return Response({'error': 'Especialidad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def obtener_horarios_por_medico(request, medico_id):
    try:
        horarios = Horario.objects.filter(medico_id=medico_id)
        horarios_data = [
            {
                'dia': horario.dia,
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M')
            } for horario in horarios
        ]
        return Response(horarios_data, status=status.HTTP_200_OK)
    except Medico.DoesNotExist:
        return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
@api_view(['POST'])
def crear_actualizar_horarios(request, medico_id):
    try:
        medico = Medico.objects.get(pk=medico_id)
        horarios = request.data.get('horarios', [])
        if not horarios:
            return Response({'error': 'Los horarios son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar horarios existentes
        Horario.objects.filter(medico=medico).delete()

        # Crear nuevos horarios
        for horario in horarios:
            Horario.objects.create(
                medico=medico,
                especialidad=medico.especialidad,
                dia=horario['dia'],
                hora_inicio=horario['hora_inicio'],
                hora_fin=horario['hora_fin']
            )
        return Response({'message': 'Horarios actualizados correctamente'}, status=status.HTTP_200_OK)
    except Medico.DoesNotExist:
        return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
@api_view(['GET'])
def obtener_especialida(request, especialidad_id):
    try:
        especialidad = Especialidad.objects.get(pk=especialidad_id)
        return Response({'nombre_especialidad': especialidad.nombre_especialidad}, status=status.HTTP_200_OK)
    except Especialidad.DoesNotExist:
        return Response({'error': 'Especialidad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
