#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..models import GoogleToken
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from apps.agenda.services.email import send_reminder_to_the_customer
import json
from django.db.models import F
from django.http import JsonResponse
from apps.profile_online.models import AppointmentOnline
from django.conf import settings
from django.core.exceptions import PermissionDenied
from ..services.calendary import update_time_appoint, EventService, get_event_detail_logic
from ..plus_wrapper import Plus
from django.db.models import F
from ..models import TypeAppoint, Appointment
from django.http import JsonResponse
import json
from django.shortcuts import render
from email import parser
import os
@login_required(login_url='login')
def agenda_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'agenda/home_agenda.html', {'PLUS_URL': settings.PLUS_URL})
    else:
        return render(request, 'agenda/home_agenda.html', {'PLUS_URL': settings.PLUS_URL})

@login_required(login_url='login')
def create_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({'success': False}, status=405)
    
        try:
            body_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'message.error.invalid-json'}, status=400)
    
        # Delegamos toda la lógica al servicio
        result = EventService.create_appointment(request.user, body_json)
    
        if result['success']:
            return JsonResponse({
                'success': True, 
                'message': 'message.success.add-new-event', 
                'event_id': result['event_id']
            }, status=201)
        else:
            # Si hubo un error de suscripción o validación, enviamos el mensaje correspondiente
            return JsonResponse(result, status=200)
    else:
        if request.method != 'POST':
            return JsonResponse({'success': False}, status=405)
    
        try:
            body_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'message.error.invalid-json'}, status=400)
    
        # Delegamos toda la lógica al servicio
        result = EventService.create_appointment(request.user, body_json)
    
        if result['success']:
            return JsonResponse({
                'success': True, 
                'message': 'message.success.add-new-event', 
                'event_id': result['event_id']
            }, status=201)
        else:
            # Si hubo un error de suscripción o validación, enviamos el mensaje correspondiente
            return JsonResponse(result, status=200)

@login_required(login_url='login')
def get_events_by_date_range(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
                return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
        try:
            # 1. get the information of the frontend
            date_start_str = request.GET.get('start_date')
            date_finish_str = request.GET.get('end_date')
            user = request.user
    
            # 2. convert the date to UTC
            start_utc = Plus.convert_to_utc(date_start_str, user.timezone)
            end_utc = Plus.convert_to_utc(date_finish_str, user.timezone)
    
            # 3. run the services
            events_data = EventService.get_calendar_events(user, start_utc, end_utc)
            return JsonResponse({'success': True, 'data': events_data}, status=200)
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        if request.method != 'GET':
                return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
        try:
            # 1. get the information of the frontend
            date_start_str = request.GET.get('start_date')
            date_finish_str = request.GET.get('end_date')
            user = request.user
    
            # 2. convert the date to UTC
            start_utc = Plus.convert_to_utc(date_start_str, user.timezone)
            end_utc = Plus.convert_to_utc(date_finish_str, user.timezone)
    
            # 3. run the services
            events_data = EventService.get_calendar_events(user, start_utc, end_utc)
            return JsonResponse({'success': True, 'data': events_data}, status=200)
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required(login_url='login')
def get_appointment_by_id(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({'success': False}, status=405)
    
        event_id = request.GET.get('id')
        if not event_id:
            return JsonResponse({'success': False, 'message': 'message.error.event-id-required'}, status=400)
    
        try:
            # Llamamos a la lógica pura
            data = get_event_detail_logic(request.user, event_id)
            
            if data:
                return JsonResponse({'success': True, 'data': data}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'message.error.event-not-found'}, status=404)
    
        except Appointment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'message.error.event-not-found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        if request.method != 'GET':
            return JsonResponse({'success': False}, status=405)
    
        event_id = request.GET.get('id')
        if not event_id:
            return JsonResponse({'success': False, 'message': 'message.error.event-id-required'}, status=400)
    
        try:
            # Llamamos a la lógica pura
            data = get_event_detail_logic(request.user, event_id)
            
            if data:
                return JsonResponse({'success': True, 'data': data}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'message.error.event-not-found'}, status=404)
    
        except Appointment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'message.error.event-not-found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required(login_url='login')
def search_events(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
        try:
            # Pasamos request.GET (diccionario de parámetros) al servicio
            events_data = EventService.search_events_logic(request.user, request.GET)
            return JsonResponse({'success': True, 'answer': events_data}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        if request.method != 'GET':
            return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
        try:
            # Pasamos request.GET (diccionario de parámetros) al servicio
            events_data = EventService.search_events_logic(request.user, request.GET)
            return JsonResponse({'success': True, 'answer': events_data}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='login')
def edit_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({'success': False}, status=405)
    
        try:
            body_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
        # Llamada al servicio
        result = EventService.update_appointment(request.user, body_json)
    
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'message.success.event-updated',
                'event_id': result['event_id']
            }, status=200)
        else:
            # Manejo de códigos de estado según el error devuelto por el servicio
            status_code = result.get('status_code', 200) # Usamos 200 por defecto para errores de lógica
            return JsonResponse(result, status=status_code)
    else:
        if request.method != 'POST':
            return JsonResponse({'success': False}, status=405)
    
        try:
            body_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
        # Llamada al servicio
        result = EventService.update_appointment(request.user, body_json)
    
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'message.success.event-updated',
                'event_id': result['event_id']
            }, status=200)
        else:
            # Manejo de códigos de estado según el error devuelto por el servicio
            status_code = result.get('status_code', 200) # Usamos 200 por defecto para errores de lógica
            return JsonResponse(result, status=status_code)

@login_required(login_url='login')
def update_appointment_time_view(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({
                "success": False,
                "message": "message.error.invalid-json",
                "error": "Invalid request method"
            }, status=400)
        
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({
                "success": False,
                "message": "message.error.invalid-json"
            }, status=400)
    
        try:
            appointment = update_time_appoint(
                user=request.user,
                appoint_id=body.get("id_event"),
                start_date=body.get("start_date"),
                start_time=body.get("start_time"),
                end_date=body.get("end_date"),
                end_time=body.get("end_time")
            )
    
            return JsonResponse({
                "success": True,
                "message": "message.success.appointment-time-updated",
                "event_id": appointment.id
            })
    
        except PermissionDenied:
            print('PermissionDenied')
            return JsonResponse({
                "success": False,
                "message": "message.error.event-not-found"
            }, status=404)
    
        except ValueError as e:
            return JsonResponse({
                "success": False,
                "message": f"message.error.{str(e)}",
                "error": str(e)
            }, status=400)
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "message.error.internal-error",
                "error": str(e)
            }, status=500)
    else:
        if request.method != 'POST':
            return JsonResponse({
                "success": False,
                "message": "message.error.invalid-json",
                "error": "Invalid request method"
            }, status=400)
        
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({
                "success": False,
                "message": "message.error.invalid-json"
            }, status=400)
    
        try:
            appointment = update_time_appoint(
                user=request.user,
                appoint_id=body.get("id_event"),
                start_date=body.get("start_date"),
                start_time=body.get("start_time"),
                end_date=body.get("end_date"),
                end_time=body.get("end_time")
            )
    
            return JsonResponse({
                "success": True,
                "message": "message.success.appointment-time-updated",
                "event_id": appointment.id
            })
    
        except PermissionDenied:
            print('PermissionDenied')
            return JsonResponse({
                "success": False,
                "message": "message.error.event-not-found"
            }, status=404)
    
        except ValueError as e:
            return JsonResponse({
                "success": False,
                "message": f"message.error.{str(e)}",
                "error": str(e)
            }, status=400)
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "message.error.internal-error",
                "error": str(e)
            }, status=500)

@login_required(login_url='login')
def delete_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
        try:
            body_json = json.loads(request.body)
            event_id = body_json.get('id_event')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
        # Ejecutar la lógica del servicio
        result = EventService.delete_appointment_logic(request.user, event_id)
    
        # Retornar respuesta basada en el resultado del servicio
        status_code = result.get('status', 200)
        return JsonResponse(result, status=status_code)
    else:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
        try:
            body_json = json.loads(request.body)
            event_id = body_json.get('id_event')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
        # Ejecutar la lógica del servicio
        result = EventService.delete_appointment_logic(request.user, event_id)
    
        # Retornar respuesta basada en el resultado del servicio
        status_code = result.get('status', 200)
        return JsonResponse(result, status=status_code)

@login_required(login_url='login')
def get_the_first_type_events(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        search_text = ""
    
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
                if isinstance(body_json, dict):
                    search_text = body_json.get("query", "").strip()
                elif isinstance(body_json, list) and len(body_json) > 0:
                    search_text = str(body_json[0]).strip()
            except Exception as e:
                print("Error parsing JSON:", e)
                search_text = ""
    
        elif request.method == 'GET':
            search_text = request.GET.get("query", "").strip()
    
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    
        # Filtramos según el texto de búsqueda si existe, o devolvemos los primeros 20
        if search_text:
            events = TypeAppoint.objects.filter(
                user=request.user,
                name__icontains=search_text
            ).annotate(
                text=F('name')
            ).values('id', 'text', 'description', 'color')[:20]
        else:
            events = TypeAppoint.objects.filter(
                user=request.user
            ).annotate(
                text=F('name')
            ).values('id', 'text', 'description', 'color')[:20]
    
        return JsonResponse({'success': True, 'answer': list(events)})
    else:
        search_text = ""
    
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
                if isinstance(body_json, dict):
                    search_text = body_json.get("query", "").strip()
                elif isinstance(body_json, list) and len(body_json) > 0:
                    search_text = str(body_json[0]).strip()
            except Exception as e:
                print("Error parsing JSON:", e)
                search_text = ""
    
        elif request.method == 'GET':
            search_text = request.GET.get("query", "").strip()
    
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    
        # Filtramos según el texto de búsqueda si existe, o devolvemos los primeros 20
        if search_text:
            events = TypeAppoint.objects.filter(
                user=request.user,
                name__icontains=search_text
            ).annotate(
                text=F('name')
            ).values('id', 'text', 'description', 'color')[:20]
        else:
            events = TypeAppoint.objects.filter(
                user=request.user
            ).annotate(
                text=F('name')
            ).values('id', 'text', 'description', 'color')[:20]
    
        return JsonResponse({'success': True, 'answer': list(events)})

@login_required(login_url='login')
def get_type_event_for_id(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET':
            type_id = request.GET.get('id')
    
            try:
                if type_id:
                    answer = TypeAppoint.objects.filter(id=type_id, user=request.user).annotate(
                        text=F('name')
                    ).values('id', 'text', 'description', 'color').first()
    
                    if not answer:
                        return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.'}, status=404)
    
                    return JsonResponse({'success': True, 'answer': answer})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al obtener el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'GET':
            type_id = request.GET.get('id')
    
            try:
                if type_id:
                    answer = TypeAppoint.objects.filter(id=type_id, user=request.user).annotate(
                        text=F('name')
                    ).values('id', 'text', 'description', 'color').first()
    
                    if not answer:
                        return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.'}, status=404)
    
                    return JsonResponse({'success': True, 'answer': answer})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al obtener el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def create_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
    
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD').strip()
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)
    
                # create and save the new TypeAppoint
                new_type = TypeAppoint(
                    name=title,
                    color=color,
                    user=request.user
                )
                new_type.save()
                
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento creado exitosamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error to create this type of event.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        data = json.loads(request.body)
    
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD').strip()
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)
    
                # create and save the new TypeAppoint
                new_type = TypeAppoint(
                    name=title,
                    color=color,
                    user=request.user
                )
                new_type.save()
                
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento creado exitosamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error to create this type of event.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def update_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
                title = data.get('title', '').strip()
                color = data.get('color', '').strip()
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'Se requiere un nombre para el tipo de evento.', 'error': 'Title is empty'}, status=400)
    
                # Verificamos que el type event exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Actualizamos los campos
                type_event.name = title
                if color:
                    type_event.color = color
                type_event.save()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento actualizado correctamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al actualizar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
                title = data.get('title', '').strip()
                color = data.get('color', '').strip()
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'Se requiere un nombre para el tipo de evento.', 'error': 'Title is empty'}, status=400)
    
                # Verificamos que el type event exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Actualizamos los campos
                type_event.name = title
                if color:
                    type_event.color = color
                type_event.save()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento actualizado correctamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al actualizar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def delete_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                # Verificamos que exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Eliminamos el tipo de evento
                type_event.delete()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento eliminado correctamente.'})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al eliminar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                # Verificamos que exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Eliminamos el tipo de evento
                type_event.delete()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento eliminado correctamente.'})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al eliminar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def setting(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'agenda/setting.html')
    else:
        return render(request, 'agenda/setting.html')

@login_required(login_url='login')
def send_reminder_for_email_to_customer(request, appoint_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': 'Método no permitido', 'error': '405'}, status=405)
    
        try:
    
            result=send_reminder_to_the_customer(appoint_id, 0)
    
            return JsonResponse({
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'error': None
            }, status=200)
    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor',
                'error': str(e)
            }, status=500)
    else:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': 'Método no permitido', 'error': '405'}, status=405)
    
        try:
    
            result=send_reminder_to_the_customer(appoint_id, 0)
    
            return JsonResponse({
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'error': None
            }, status=200)
    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor',
                'error': str(e)
            }, status=500)

@login_required(login_url='login')
def google_sync(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        flow = Flow.from_client_secrets_file(
            os.path.join(os.path.dirname(__file__), 'credentials.json'), #the credentials is in the folder config 
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri=f"http://{settings.PLUS_URL}/agenda/oauth2callback"  # Cambiado a callback
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
    
        request.session['oauth_state'] = state
        return redirect(authorization_url)
    else:
        flow = Flow.from_client_secrets_file(
            os.path.join(os.path.dirname(__file__), 'credentials.json'), #the credentials is in the folder config 
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri=f"http://{settings.PLUS_URL}/agenda/oauth2callback"  # Cambiado a callback
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
    
        request.session['oauth_state'] = state
        return redirect(authorization_url)

@login_required(login_url='login')
def oauth2callback(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #QUITAR EN PRODUCCION
        flow = Flow.from_client_secrets_file(
            os.path.join(os.path.dirname(__file__), 'credentials.json'), #the credentials is in the folder config 
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri=f"http://{settings.PLUS_URL}/agenda/oauth2callback"
        )
    
        # Esta URL contiene el código que Google envía tras autorizar al usuario
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
    
        # Guardar en DB para el usuario actual
        defaults = {
            'token': credentials.token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': ",".join(credentials.scopes),
        }
    
        # Solo agregar refresh_token si existe
        if credentials.refresh_token:
            defaults['refresh_token'] = credentials.refresh_token
    
        GoogleToken.objects.update_or_create(
            user=request.user,
            defaults=defaults
        )
    
        return render(request, 'success_sync.html')
    else:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #QUITAR EN PRODUCCION
        flow = Flow.from_client_secrets_file(
            os.path.join(os.path.dirname(__file__), 'credentials.json'), #the credentials is in the folder config 
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri=f"http://{settings.PLUS_URL}/agenda/oauth2callback"
        )
    
        # Esta URL contiene el código que Google envía tras autorizar al usuario
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
    
        # Guardar en DB para el usuario actual
        defaults = {
            'token': credentials.token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': ",".join(credentials.scopes),
        }
    
        # Solo agregar refresh_token si existe
        if credentials.refresh_token:
            defaults['refresh_token'] = credentials.refresh_token
    
        GoogleToken.objects.update_or_create(
            user=request.user,
            defaults=defaults
        )
    
        return render(request, 'success_sync.html')

