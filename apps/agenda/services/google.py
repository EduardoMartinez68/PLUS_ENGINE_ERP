from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ..models import GoogleToken
from django.utils import timezone
from datetime import datetime, timedelta, time


def get_credential_google_calendar(user):
    try:
        # Recuperar el token guardado en DB
        token_obj = GoogleToken.objects.get(user=user)
        
        creds = Credentials(
            token=token_obj.token,
            refresh_token=token_obj.refresh_token,
            token_uri=token_obj.token_uri,
            client_id=token_obj.client_id,
            client_secret=token_obj.client_secret,
            scopes=token_obj.scopes.split(",")
        ) 

        return creds
    except GoogleToken.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error when try get the token of Google calendar: {e}")
        return None
    
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from datetime import datetime

def obtener_eventos_google(user, start_date, end_date):
    creds = get_credential_google_calendar(user)
    if not creds:
        return []

    try:
        service = build('calendar', 'v3', credentials=creds)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

    except RefreshError:
        # Token expirado o revocado, devolver lista vacía
        print(f"Google token expired or revoked for user {user}")
        return []
    except Exception as e:
        # Cualquier otro error en la API
        print(f"Error fetching Google events: {e}")
        return []

    events = events_result.get('items', [])

    google_events = []
    for e in events:
        try:
            start = e['start'].get('dateTime') or e['start'].get('date')
            end = e['end'].get('dateTime') or e['end'].get('date')

            # parsear a datetime con tzinfo
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)

            google_events.append({
                'id': e['id'],
                'title': e.get('summary', ''),
                'description': e.get('description', ''),
                'date_start': start_dt.isoformat(),
                'date_finish': end_dt.isoformat(),
                'location': e.get('location', ''),
                'emails_guests': ','.join([a['email'] for a in e.get('attendees', [])]) if e.get('attendees') else '',
                'source': 'google'
            })
        except Exception as ex:
            print(f"Error parsing Google event: {ex}")
            continue

    return google_events


def get_appoint_from_google_with_id(user, event_id):
    """
    Obtiene un evento de Google Calendar por su ID y lo transforma
    a un formato compatible con el modelo Appointment.
    """
    creds = get_credential_google_calendar(user)
    if not creds:
        return None

    service = build('calendar', 'v3', credentials=creds)

    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        start = event['start'].get('dateTime') or event['start'].get('date')
        end = event['end'].get('dateTime') or event['end'].get('date')

        # parsear a datetime con tzinfo
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Mapeo a formato compatible con Appointment
        appoint_data = {
            "name_event": event.get("summary", ""),
            "description": event.get("description", ""),
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "start_time": start_dt.strftime("%H:%M"),
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "end_time": end_dt.strftime("%H:%M"),
            "emails_guests": [a['email'] for a in event.get('attendees', [])] if event.get('attendees') else [],
            "location": event.get("location", ""),
            "link": "",  # opcional, no viene de Google
            "alert_time": 0,  # puedes definir default o extraer de evento si tienes notificaciones
            "priority": 0,  # default
            "activate_event_all_the_day": False,
            "repeat_this_event": False,
            "time_repeat": 0,
            "time_end_repeat": None,
            "send_notification": True,
            "i_am_free": True,
            "type_event": None,  # opcional, puedes mapear a un tipo
            "id_event_in_google_calendar": event["id"]
        }

        return appoint_data

    except Exception as ex:
        print(f"Error obteniendo evento de Google: {ex}")
        return None

def get_appoints_from_google_with_title(user, title_event, start_date=None, end_date=None, limit=5):
    """
    Busca eventos en Google Calendar por título similar (no exacto).
    Devuelve hasta `limit` eventos.
    """
    creds = get_credential_google_calendar(user)
    if not creds:
        return []

    service = build('calendar', 'v3', credentials=creds)

    # Si no se define rango de fechas, usamos hoy +/- 1 año
    now = timezone.now()
    if not start_date:
        start_date = now - timedelta(days=365)
    if not end_date:
        end_date = now + timedelta(days=365)

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime',
            q=title_event  # búsqueda por texto parcial
        ).execute()

        events = events_result.get('items', [])

        # Limitar a `limit` resultados
        events = events[:limit]

        appoints = []
        for event in events:
            start = event['start'].get('dateTime') or event['start'].get('date')
            end = event['end'].get('dateTime') or event['end'].get('date')

            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)

            appoint_data = {
                "name_event": event.get("summary", ""),
                "description": event.get("description", ""),
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "start_time": start_dt.strftime("%H:%M"),
                "end_date": end_dt.strftime("%Y-%m-%d"),
                "end_time": end_dt.strftime("%H:%M"),
                "emails_guests": [a['email'] for a in event.get('attendees', [])] if event.get('attendees') else [],
                "location": event.get("location", ""),
                "link": "",
                "alert_time": 0,
                "priority": 0,
                "activate_event_all_the_day": False,
                "repeat_this_event": False,
                "time_repeat": 0,
                "time_end_repeat": None,
                "send_notification": True,
                "i_am_free": True,
                "type_event": None,
                "id_event_in_google_calendar": event["id"]
            }
            appoints.append(appoint_data)

        return appoints

    except Exception as ex:
        print(f"Error buscando eventos por título en Google: {ex}")
        return []

def crear_evento_google(user, title, description, date_start, date_finish, time_alert, repeat_this_event, time_repeat, emails_guests):
    creds = get_credential_google_calendar(user)

    if not creds:
        return None
    
    try:
        # Recuperar el token guardado en DB
        service = build('calendar', 'v3', credentials=creds)

        # Definir el evento
        evento = {
            'summary': title,          # título del evento
            'description': description,  # descripción
            'start': {
                'dateTime': date_start.isoformat(),      # formato ISO: "2025-09-20T10:00:00-06:00"
                'timeZone': user.timezone,
            },
            'end': {
                'dateTime': date_finish.isoformat(),         # formato ISO: "2025-09-20T11:00:00-06:00"
                'timeZone': user.timezone,
            },
            'reminders': {
                'useDefault': False,  # si pones True usa los recordatorios por defecto de Google Calendar
                'overrides': [
                    {'method': 'popup', 'minutes': time_alert},  # notificación 15 minutos antes
                    {'method': 'email', 'minutes': 30}
                ],
            }
        }

        #here we will do a event that can repat 
        if repeat_this_event:
            if time_repeat > 0:
                # Ejemplo: repetir cada X días
                evento['recurrence'] = [f'RRULE:FREQ=DAILY;INTERVAL={time_repeat}']
            else:
                # Si no se especifica intervalo, por default semanal
                evento['recurrence'] = ['RRULE:FREQ=WEEKLY;BYDAY=MO']

        #add the event of the email for send notification for email
        if emails_guests:
            lista_emails = [email.strip() for email in emails_guests.split(',')]
            evento['attendees'] = [{'email': email} for email in lista_emails]

        # Insertar el evento en Google Calendar
        creado = service.events().insert(calendarId='primary', body=evento).execute()
        event_id = creado.get("id")
        return event_id
    
    except Exception as e:
        print("Error creando evento en Google Calendar:", e)
        return None
    except GoogleToken.DoesNotExist:
        return None
    
import re
def is_valid_email(email):
    # Simple regex para validar email
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def update_event_in_google_calendar(user,event_id,new_title=None,new_description=None,new_date_start=None,new_date_finish=None,new_time_alert=None,repeat_this_event=None,time_repeat=None,emails_guests=None):
    if not event_id:
        return None
    
    
    try:
        # Recuperar el token guardado en DB    
        creds = get_credential_google_calendar(user)
        if not creds:
            return None    
        service = build('calendar', 'v3', credentials=creds)
        # Obtener el evento actual
        evento_existente = service.events().get(calendarId='primary', eventId=event_id).execute()

        # Actualizar campos si se pasaron nuevos valores
        if new_title:
            evento_existente['summary'] = new_title
        if new_description:
            evento_existente['description'] = new_description
        if new_date_start and new_date_finish:
            evento_existente['start'] = {
                'dateTime': new_date_start.isoformat(),
                'timeZone': user.timezone,
            }
            evento_existente['end'] = {
                'dateTime': new_date_finish.isoformat(),
                'timeZone': user.timezone,
            }
        if new_time_alert is not None:
            evento_existente['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': new_time_alert},
                    {'method': 'email', 'minutes': 30}
                ],
            }

        # Repetición
        if repeat_this_event is False:
            # Si se pasa False, eliminamos la repetición
            evento_existente.pop('recurrence', None)
        elif repeat_this_event is not None:
            if time_repeat and int(time_repeat) > 0:
                evento_existente['recurrence'] = [f'RRULE:FREQ=DAILY;INTERVAL={int(time_repeat)}']
            else:
                evento_existente['recurrence'] = ['RRULE:FREQ=WEEKLY;BYDAY=MO']


        # Invitados
        if emails_guests:
            lista_emails = [email.strip() for email in emails_guests.split(',')]
            # filtra solo los válidos
            lista_emails_validos = [email for email in lista_emails if is_valid_email(email)]
            if lista_emails_validos:
                evento['attendees'] = [{'email': email} for email in lista_emails_validos]

        # Guardar cambios en Google Calendar
        actualizado = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=evento_existente
        ).execute()

        return actualizado

    except GoogleToken.DoesNotExist:
        return None
    
def delete_event_in_google_calendar(user, event_id):
    if not event_id:
        return None
    
    creds = get_credential_google_calendar(user)
    if not creds:
        return None
    
    try:
        # Recuperar el token guardado en DB        
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
    except GoogleToken.DoesNotExist:
        return None