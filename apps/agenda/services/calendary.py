from datetime import timedelta, datetime, time
from django.http import JsonResponse
from ..plus_wrapper import Plus
from ..models import TypeAppoint, Appointment
from apps.profile_online.models import AppointmentOnline
from apps.customers.models import Customer
from django.core.exceptions import PermissionDenied
from django.utils.timezone import localtime
from ..services.google import obtener_eventos_google, get_appoint_from_google_with_id, crear_evento_google, get_appoints_from_google_with_title, update_event_in_google_calendar, delete_event_in_google_calendar
from django.db.models import Q
import threading

def create_new_appointment(data: dict, user):
    """
    Crea un evento/appointment a partir de un diccionario de datos y un usuario.
    Devuelve un dict con 'success' y 'event_id' o 'message' en caso de error.
    """
    def validate_date_range(start: datetime, end: datetime) -> bool:
        return start <= end

    try:
        # Fechas del evento
        date_start = datetime.strptime(f"{data.get('start_date')} {data.get('start_time')}", "%Y-%m-%d %H:%M")
        date_finish = datetime.strptime(f"{data.get('end_date')} {data.get('end_time')}", "%Y-%m-%d %H:%M")

        # Convertir a UTC según zona horaria del usuario
        timezone = user.timezone
        date_start_utc = Plus.convert_to_utc(date_start, timezone)
        date_finish_utc = Plus.convert_to_utc(date_finish, timezone)

        if not validate_date_range(date_start_utc, date_finish_utc):
            return {'success': False, 'message': 'message.error.invalid-date-range'}

        # Manejo de repetición
        time_repeat = int(data.get("time_repeat", 0) or 0)
        time_end_repeat = data.get("time_end_repeat")
        finish_repeat_date = None
        if time_end_repeat is not None:
            try:
                finish_repeat_date = date_start_utc + timedelta(days=int(time_end_repeat))
            except ValueError:
                finish_repeat_date = None

        # Agregar evento a Google Calendar si hay token
         

        # Crear Appointment en DB
        appointment = Appointment.objects.create(
            title=data.get("name_event", ""),
            description=data.get("description", ""),
            date_start=date_start_utc,
            date_finish=date_finish_utc,
            time_alert=int(data.get("alert_time", 0)),
            priority=int(data.get("priority", 0)),
            activate_event_all_the_day=data.get("activate_event_all_the_day") == "on",
            emails_guests=data.get("emails_guests", []),
            location=data.get("location", ""),
            link=data.get("link", ""),
            repeat_this_event=data.get("repeat_this_event") == "on",
            time_repeat=time_repeat,
            finish_repeat_date=finish_repeat_date,
            send_notification=data.get("send_notification") == "on",
            i_am_free=data.get("i_am_free") == "on",
            id_type_appoint_id=data.get("type_event"),
            id_event_in_google_calendar=data.get("id_event_in_google_calendar"),
            user=user
        )

        return {'success': True, 'event_id': appointment.id}

    except Exception as e:
        print("Error creating appointment:", e)
        return {'success': False, 'message': 'message.success.not-can-add-new-event', 'error': str(e)}
    
def update_time_appoint(*, user, appoint_id, start_date, start_time, end_date, end_time):
    """
    Actualiza SOLO la hora de una cita.
    - Valida que la cita sea del usuario
    - Convierte a UTC según timezone del usuario
    - Valida rango de fechas
    """

    # Convertir a datetime local
    try:
        start_local = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_local = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("invalid-date-format")

    # Validar rango
    if start_local >= end_local:
        raise ValueError("invalid-date-range")

    # Convertir a UTC
    start_utc = Plus.convert_to_utc(start_local, user.timezone)
    end_utc = Plus.convert_to_utc(end_local, user.timezone)

    # Obtener cita (ownership check)
    try:
        appointment = Appointment.objects.get(id=appoint_id, user=user)
    except Appointment.DoesNotExist:
        raise PermissionDenied("appointment-not-found-or-not-owned")


    # Actualizar solo lo necesario
    appointment.date_start = start_utc
    appointment.date_finish = end_utc
    appointment.reminder_sent = False  # opcional: fuerza re-notificación
    appointment.status=Appointment.PENDING
    appointment.save(update_fields=["date_start", "date_finish", "reminder_sent", "status"])
    sync_online_appointment_status(appointment)


    #now we will see if this event have an id in google calendar for update 
    if appointment.id_event_in_google_calendar:
        thread = threading.Thread(
            target=update_event_in_google_calendar, 
            args=(
                user, 
                appointment.id_event_in_google_calendar,
                appointment.title,
                appointment.description,
                appointment.date_start,
                appointment.date_finish,
                appointment.time_alert,
                appointment.repeat_this_event,
                appointment.time_repeat,
                appointment.emails_guests
            )
        )
        thread.start()

    #now we will send a email to the customer for that the patient know that the doctor change the date of the apppoint
    from .email import send_reminder_to_the_customer
    send_reminder_to_the_customer(appointment, 1)

    return appointment

def sync_online_appointment_status(appointment_obj):
    """
    Sincroniza el estado de Appointment con AppointmentOnline si existe.
    """
    if not appointment_obj.online_appointment_id:
        return None

    # Mapeo de estados: Agenda -> Online
    # 'P' -> pending, 'C' -> confirmed, 'X' -> cancelled
    status_mapping = {
        appointment_obj.PENDING: 'pending',
        appointment_obj.CONFIRMED: 'confirmed',
        appointment_obj.CANCELLED: 'cancelled',
    }

    new_status = status_mapping.get(appointment_obj.status)

    if new_status:
        try:
            from apps.profile_online.models import AppointmentOnline
            # Actualizamos directamente en la base de datos
            AppointmentOnline.objects.filter(id=appointment_obj.online_appointment_id).update(
                status=new_status
            )
        except Exception as e:
            print(f"Error sincronizando cita online {appointment_obj.online_appointment_id}: {e}")


def get_event_detail_logic(user, event_id_raw):
    """
    Lógica para obtener un evento. 
    Si el ID es de Google, sincroniza con la DB. 
    Retorna un diccionario con la data o None si falla.
    """    
    event = None

    # 1. Identificar si el ID es interno (numérico) o de Google (string)
    try:
        # Intentamos convertir a int para ver si es ID de nuestra base de datos
        internal_id = int(event_id_raw)
        event = Appointment.objects.select_related('id_type_appoint', 'customer').get(
            id=internal_id, 
            user=user
        )
    except (ValueError, TypeError):
        # Si falla la conversión, es un ID de Google
        google_id = event_id_raw
        
        # Primero buscamos si ya existe en nuestra DB por su ID de Google
        event = Appointment.objects.filter(
            id_event_in_google_calendar=google_id, 
            user=user
        ).select_related('id_type_appoint', 'customer').first()

        # Si no existe, lo traemos de la API y lo creamos localmente
        if not event:
            event_data = get_appoint_from_google_with_id(user, google_id)
            answer = create_new_appointment(event_data, user)
            
            if answer.get("success"):
                event = Appointment.objects.select_related('id_type_appoint', 'customer').get(id=answer["event_id"])
            else:
                return None # No se pudo encontrar ni crear

    # 2. Procesar fechas y Serializar
    if event:
        # Convertimos las fechas de UTC a la zona horaria del usuario
        date_start_local = Plus.convert_from_utc(event.date_start, user.timezone)
        date_finish_local = Plus.convert_from_utc(event.date_finish, user.timezone)

        # Lógica de cliente/cita online
        c_name, c_email, c_whatsapp = '', '', ''
        if event.customer:
            c_name, c_email, c_whatsapp = event.customer.name, event.customer.email, event.customer.cellphone
        elif event.online_appointment_id:
            online = AppointmentOnline.objects.filter(id=event.online_appointment_id).first()
            if online:
                c_name, c_email, c_whatsapp = online.customer_name, online.customer_email, online.patient_whatsapp

        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date_start': date_start_local.isoformat(),
            'date_finish': date_finish_local.isoformat(),
            'time_alert': event.time_alert,
            'priority': event.priority,
            'activate_event_all_the_day': event.activate_event_all_the_day,
            'emails_guests': event.emails_guests,
            'location': event.location,
            'link': event.link,
            'repeat_this_event': event.repeat_this_event,
            'time_repeat': event.time_repeat,
            'finish_repeat_date': event.finish_repeat_date.isoformat() if event.finish_repeat_date else None,
            'send_notification': event.send_notification,
            'i_am_free': event.i_am_free,
            'status': event.status,
            'customer': {
                'id': event.customer.id if event.customer else None,
                'name': event.customer.name if event.customer else None,
            },
            'type_appoint': {
                'id': event.id_type_appoint.id if event.id_type_appoint else None,
                'name': event.id_type_appoint.name if event.id_type_appoint else None,
                'description': event.id_type_appoint.description if event.id_type_appoint else None,
                'color': event.id_type_appoint.color if event.id_type_appoint else None,
            },

            #this are the data of the appoint for send record
            'customer_name': c_name,
            'customer_email': c_email,
            'customer_whatsapp': c_whatsapp
        }
    
    return None

#-------------------------------THIS IS FOR GET ALL THE APPPOINTS IN A RANGE OF DATE------------------------
from dateutil.relativedelta import relativedelta

class EventService:
    #----------------------this is for get all the appoints in a range of date------------------------------
    @staticmethod
    def serialize_event(e, date_start, date_finish):
        """Transforma un objeto Appointment en un diccionario para el frontend."""
        return {
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'date_start': localtime(date_start).isoformat(),
            'date_finish': localtime(date_finish).isoformat(),
            'time_alert': e.time_alert,
            'priority': e.priority,
            'activate_event_all_the_day': e.activate_event_all_the_day,
            'emails_guests': e.emails_guests,
            'location': e.location,
            'link': e.link,
            'repeat_this_event': e.repeat_this_event,
            'time_repeat': e.time_repeat,
            'finish_repeat_date': e.finish_repeat_date.isoformat() if e.finish_repeat_date else None,
            'send_notification': e.send_notification,
            'status': e.status,
            'i_am_free': e.i_am_free,
            'type_appoint': {
                'id': e.id_type_appoint.id if e.id_type_appoint else None,
                'name': e.id_type_appoint.name if e.id_type_appoint else None,
                'color': e.id_type_appoint.color if e.id_type_appoint else None,
            }
        }

    @staticmethod
    def chunk_multiday_event(e, date_start, date_finish):
        """Divide un evento que dura varios días en fragmentos por día."""
        events_data = []
        if date_start.date() == date_finish.date():
            events_data.append(EventService.serialize_event(e, date_start, date_finish))
        else:
            current_date = date_start.date()
            while current_date <= date_finish.date():
                if current_date == date_start.date():
                    s_time = date_start.time()
                else:
                    s_time = time(0, 0)

                if current_date == date_finish.date():
                    e_time = date_finish.time()
                else:
                    e_time = time(23, 59, 59)

                chunk_start = datetime.combine(current_date, s_time, tzinfo=date_start.tzinfo)
                chunk_end = datetime.combine(current_date, e_time, tzinfo=date_start.tzinfo)
                
                events_data.append(EventService.serialize_event(e, chunk_start, chunk_end))
                current_date += timedelta(days=1)
        return events_data

    @classmethod
    def get_calendar_events(cls, user, start_range, end_range):
        """Lógica principal para obtener y mezclar eventos sin duplicados."""
        final_events = []
        # Usamos un set para trackear IDs de Google ya procesados desde nuestra DB
        seen_google_ids = set()

        # 1. Obtener eventos normales y recurrentes de la DB local
        db_events = Appointment.objects.filter(
            user=user,
            date_start__lte=end_range,
            date_finish__gte=start_range
        ).select_related('id_type_appoint')

        for e in db_events:
            # get the id of the event of google in the appoint
            if hasattr(e, 'id_event_in_google_calendar') and e.id_event_in_google_calendar:
                seen_google_ids.add(e.id_event_in_google_calendar)
            
            d_start = Plus.convert_from_utc(e.date_start, user.timezone)
            d_finish = Plus.convert_from_utc(e.date_finish, user.timezone)
            final_events += cls.chunk_multiday_event(e, d_start, d_finish)

        # 3. Obtener eventos de Google API
        google_list = obtener_eventos_google(user, start_range, end_range)
        
        for g_event in google_list:
            # SOLUCIÓN AL DUPLICADO:
            # Asumiendo que g_event tiene un 'id' que es el de Google
            if g_event.get('id') not in seen_google_ids:
                final_events.append(g_event)

        return final_events
    
    #-------------------this is for create , update or delete appoints------------------
    @staticmethod
    def process_event_dates(user, data):
        """Convierte fechas/horas de string a UTC."""
        date_start_str = f"{data.get('start_date', '')} {data.get('start_time', '')}"
        date_finish_str = f"{data.get('end_date', '')} {data.get('end_time', '')}"

        try:
            date_start = datetime.strptime(date_start_str, "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(date_finish_str, "%Y-%m-%d %H:%M")
            
            # Convertimos a UTC usando tu helper
            return {
                'start': Plus.convert_to_utc(date_start, user.timezone),
                'end': Plus.convert_to_utc(date_finish, user.timezone)
            }
        except ValueError:
            return None

    @classmethod
    def create_appointment(cls, user, data):
        """Lógica de negocio completa para crear un evento."""
        
        # 1. Validación de Suscripción
        sub = Plus.valid_subscription(user, 'appointments')
        if not sub.get("status", False):
            return {"success": False, "message": sub.get("message"), "error_code": "SUBSCRIPTION_ERROR"}

        # 2. Validación de Campos Básicos
        title = data.get("name_event", "").strip()
        if not title:
            return {"success": False, "message": "message.error.need-a-name-for-your-event"}

        # 3. Procesar Fechas
        dates = cls.process_event_dates(user, data)
        if not dates or dates['start'] > dates['end']:
            return {"success": False, "message": "message.error.invalid-date-range"}

        # 4. Calcular repetición
        date_end_repeat = None
        time_end_repeat = data.get("time_end_repeat")
        if time_end_repeat:
            try:
                date_end_repeat = dates['start'] + timedelta(days=int(time_end_repeat))
            except (ValueError, TypeError):
                pass

        # 5. Obtener Cliente
        customer_id = data.get("customer")
        customer = Customer.objects.filter(pk=customer_id).first() if customer_id else None

        # 6. Sincronizar con Google Calendar
        google_id = crear_evento_google(
            user, title, data.get("description", ""), 
            dates['start'], dates['end'], 
            data.get("alert_time") or 0, 
            data.get("repeat_this_event") == "on", 
            data.get("time_repeat") or 0, 
            data.get("emails_guests", [])
        )

        # 7. Crear en Base de Datos Local
        try:
            appointment = Appointment.objects.create(
                user=user,
                title=title,
                description=data.get("description", ""),
                date_start=dates['start'],
                date_finish=dates['end'],
                time_alert=int(data.get("alert_time") or 0),
                priority=int(data.get("priority") or 0),
                activate_event_all_the_day=data.get("activate_event_all_the_day") == "on",
                emails_guests=data.get("emails_guests", []),
                location=data.get("location", ""),
                link=data.get("link", ""),
                repeat_this_event=data.get("repeat_this_event") == "on",
                time_repeat=int(data.get("time_repeat") or 0),
                finish_repeat_date=date_end_repeat,
                send_notification=data.get("send_notification") == "on",
                i_am_free=data.get("i_am_free") == "on",
                id_type_appoint_id=data.get("type_event"),
                id_event_in_google_calendar=google_id,
                customer=customer
            )
            return {"success": True, "event_id": appointment.id}
        except Exception as e:
            return {"success": False, "message": "message.success.not-can-add-new-event", "error": str(e)}
    
    @classmethod
    def update_appointment(cls, user, data):
        """Lógica de negocio para editar un evento existente."""
        event_id = data.get('id_event')
        title = data.get("name_event", "").strip()

        # 1. Validaciones básicas
        if not event_id:
            return {"success": False, "message": "message.error.event-id-required"}
        if not title:
            return {"success": False, "message": "message.error.need-a-name-for-your-event"}

        # 2. Procesar Fechas (usando los campos de edición del JSON)
        # Adaptamos los keys del JSON para reutilizar la lógica de procesamiento de fechas
        date_payload = {
            'start_date': data.get("start_date_edit"),
            'start_time': data.get("start_time_edit"),
            'end_date': data.get("end_date_edit"),
            'end_time': data.get("end_time_edit")
        }
        dates = cls.process_event_dates(user, date_payload)
        
        if not dates or dates['start'] > dates['end']:
            return {"success": False, "message": "message.error.invalid-date-range"}

        # 3. Calcular fin de repetición
        date_end_repeat = None
        time_end_repeat = data.get("time_end_repeat", "0")
        if time_end_repeat != '0':
            try:
                date_end_repeat = dates['start'] + timedelta(days=int(time_end_repeat))
            except (ValueError, TypeError): pass


        try:
            # 4. Obtener y actualizar instancia local
            appointment = Appointment.objects.get(id=event_id, user=user)
            
            #get the old time of the appoint. This is for know if the appoint was change in his time.
            #if the appoint was change in his time we will send a recover to the customer
            old_date_start=appointment.date_start 
            old_date_finish=appointment.date_finish

            # Obtener cliente si cambió
            customer_id = data.get("customer")
            customer = Customer.objects.filter(pk=customer_id).first() if customer_id else None

            # Actualización de campos
            appointment.title = title
            appointment.description = data.get("description", "")
            appointment.date_start = dates['start']
            appointment.date_finish = dates['end']
            appointment.time_alert = int(data.get("alert_time") or 0)
            appointment.priority = int(data.get("priority") or 0)
            appointment.activate_event_all_the_day = data.get("activate_event_all_the_day") == "on"
            appointment.emails_guests = data.get("emails_guests", [])
            appointment.location = data.get("location", "")
            appointment.link = data.get("link", "")
            appointment.repeat_this_event = data.get("repeat_this_event") == "on"
            appointment.time_repeat = int(data.get("time_repeat") or 0)
            appointment.finish_repeat_date = date_end_repeat
            appointment.send_notification = data.get("send_notification") == "on"
            appointment.i_am_free = data.get("i_am_free") == "on"
            appointment.customer = customer
            appointment.id_type_appoint_id = data.get("type_event")
            appointment.status = data.get("status", "P")
            
            appointment.save()

            # 5. Sincronizaciones externas
            sync_online_appointment_status(appointment) # Tu función externa
            
            if appointment.id_event_in_google_calendar:
                thread = threading.Thread(
                    target=update_event_in_google_calendar, 
                    args=(
                        user, 
                        appointment.id_event_in_google_calendar,
                        appointment.title,
                        appointment.description,
                        dates['start'], 
                        dates['end'],
                        appointment.time_alert,
                        appointment.repeat_this_event,
                        appointment.time_repeat,
                        appointment.emails_guests
                    )
                )
                thread.start()

            #now we will send a email to the customer for that the patient know that the doctor change the date of the apppoint
            #this only can be send when the time was change 
            if old_date_start!=appointment.date_start or old_date_finish!=appointment.date_finish:
                from .email import send_reminder_to_the_customer
                send_reminder_to_the_customer(appointment, 1)

            return {"success": True, "event_id": appointment.id}

        except Appointment.DoesNotExist:
            return {"success": False, "message": "message.error.event-not-found", "status_code": 404}
        except Exception as e:
            return {"success": False, "message": "message.error.cannot-update-event", "error": str(e), "status_code": 500}
    
    @classmethod
    def delete_appointment_logic(cls, user, event_id_raw):
        """
        Elimina un evento localmente (incluyendo AppointmentOnline) 
        y en Google Calendar.
        """
        if not event_id_raw:
            return {"success": False, "message": "message.error.no-event-id-provided", "status": 400}

        google_id_to_delete = None
        
        # 1. Intentar identificar el tipo de ID
        try:
            internal_id = int(event_id_raw)
            # Caso A: Es un ID numérico de nuestra base de datos
            appointment = Appointment.objects.filter(id=internal_id, user=user).first()
            if appointment:
                google_id_to_delete = appointment.id_event_in_google_calendar
                
                # Limpiar cita online si existe
                if appointment.online_appointment_id:
                    AppointmentOnline.objects.filter(id=appointment.online_appointment_id).delete()
                
                appointment.delete()
            else:
                return {"success": False, "message": "message.error.event-not-found", "status": 404}

        except (ValueError, TypeError):
            # Caso B: Es un String (ID de Google Calendar)
            google_id_to_delete = event_id_raw
            
            # Verificamos si este evento de Google está vinculado a algo local
            existing_event = Appointment.objects.filter(
                id_event_in_google_calendar=google_id_to_delete, 
                user=user
            ).first()
            
            if existing_event:
                if existing_event.online_appointment_id:
                    AppointmentOnline.objects.filter(id=existing_event.online_appointment_id).delete()
                existing_event.delete()

        # 2. Eliminar en Google Calendar (si tenemos un ID válido)
        if google_id_to_delete:
            try:
                delete_event_in_google_calendar(user, google_id_to_delete)
            except Exception as e:
                # Logueamos el error pero no detenemos el éxito local
                print(f"Error deleting from Google: {e}")

        return {"success": True, "message": "message.success.event-deleted"}
    #-------------------------------this is for search events in the history-------------------------
    @staticmethod
    def _serialize_search_result(e, user):
        """Helper para serializar citas de la DB local."""
        d_start = Plus.convert_from_utc(e.date_start, user.timezone)
        d_finish = Plus.convert_from_utc(e.date_finish, user.timezone)
        
        # Lógica de estrellas
        priority_stars = '★' * (e.priority + 1)

        # Lógica de cliente/cita online
        c_name, c_email, c_whatsapp = '', '', ''
        if e.customer:
            c_name, c_email, c_whatsapp = e.customer.name, e.customer.email, e.customer.cellphone
        elif e.online_appointment_id:
            online = AppointmentOnline.objects.filter(id=e.online_appointment_id).first()
            if online:
                c_name, c_email, c_whatsapp = online.customer_name, online.customer_email, online.patient_whatsapp

        return {
            'id': e.id,
            'title': e.title,
            'date_start': Plus.format_date_to_text(d_start.isoformat(), user.language, 1),
            'date_finish': Plus.format_date_to_text(d_finish.isoformat(), user.language, 1),
            'priority': priority_stars,
            'customer_name': c_name,
            'customer_email': c_email,
            'customer_whatsapp': c_whatsapp,
            "type_appoint_name": e.id_type_appoint.name if e.id_type_appoint else None,
            "type_appoint_color": e.id_type_appoint.color if e.id_type_appoint else '#91BBEA',
            "status": e.status,
            "source": "local"
        }

    @staticmethod
    def _serialize_google_search_result(g, user):
        """Helper para serializar citas que vienen de Google."""
        # Convertir strings de Google a datetime y luego a local
        dt_s = datetime.strptime(f"{g['start_date']} {g['start_time']}", "%Y-%m-%d %H:%M")
        dt_f = datetime.strptime(f"{g['end_date']} {g['end_time']}", "%Y-%m-%d %H:%M")
        
        loc_s = Plus.convert_from_utc(dt_s, user.timezone)
        loc_f = Plus.convert_from_utc(dt_f, user.timezone)

        return {
            'id': str(g['id_event_in_google_calendar']),
            'title': f"{g['name_event']} [google]",
            'date_start': Plus.format_date_to_text(loc_s.isoformat(), user.language, 2),
            'date_finish': Plus.format_date_to_text(loc_f.isoformat(), user.language, 2),
            'priority': '⭐',
            'source': 'google',
            "type_appoint_color": "#91BBEA"
        }
    
    @classmethod
    def search_events_logic(cls, user, params):
        """
        Busca eventos locales y de Google, filtra duplicados y serializa.
        """
        # 1. Extraer y preparar filtros
        all_filters = params.get('allFilters', '').strip()
        filters = [f.strip() for f in all_filters.split(',') if f] if all_filters else []
        
        search = params.get('query') or (filters[0] if filters else '')
        type_event_id = filters[1] if len(filters) > 1 else None
        start_date = params.get('start_date')
        end_date = params.get('end_date')

        # 2. Query Base Local
        events_qs = Appointment.objects.filter(user=user).select_related('id_type_appoint', 'customer')

        if start_date and end_date:
            start_utc = Plus.convert_to_utc(start_date, user.timezone)
            end_utc = Plus.convert_to_utc(end_date, user.timezone)
            events_qs = events_qs.filter(date_start__lte=end_utc, date_finish__gte=start_utc)

        if search:
            events_qs = events_qs.filter(Q(title__icontains=search) | Q(description__icontains=search)).order_by('date_start')
        else:
            events_qs = events_qs.order_by('-date_start')

        if type_event_id:
            try:
                events_qs = events_qs.filter(id_type_appoint_id=int(type_event_id))
            except ValueError: pass

        # Limitar y ejecutar
        local_events = list(events_qs[:20])
        events_data = []
        seen_google_ids = set()

        # 3. Serializar Locales
        for e in local_events:
            if e.id_event_in_google_calendar:
                seen_google_ids.add(e.id_event_in_google_calendar)
            
            events_data.append(cls._serialize_search_result(e, user))

        # 4. Integración con Google (Diferencia de 20 - actuales)
        if len(events_data) < 20:
            google_raw = get_appoints_from_google_with_title(user, search)
            for g in google_raw:
                if g['id_event_in_google_calendar'] not in seen_google_ids:
                    events_data.append(cls._serialize_google_search_result(g, user))
                    if len(events_data) >= 20: break

        return events_data