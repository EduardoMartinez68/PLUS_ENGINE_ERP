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
        print(f"No se encontró token para el usuario {user}")
        return None
    except Exception as e:
        print(f"Error obteniendo credenciales de Google Calendar: {e}")
        return None
    
def obtener_eventos_google(user, start_date, end_date):
    creds = get_credential_google_calendar(user)
    if not creds:
        return []

    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_date.isoformat(),
        timeMax=end_date.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

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
    
    creds = get_credential_google_calendar(user)
    if not creds:
        return None
    
    try:
        # Recuperar el token guardado en DB        
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
        if repeat_this_event is not None:
            if time_repeat and int(time_repeat) > 0:
                evento_existente['recurrence'] = [f'RRULE:FREQ=DAILY;INTERVAL={int(time_repeat)}']
            else:
                evento_existente['recurrence'] = ['RRULE:FREQ=WEEKLY;BYDAY=MO']
        elif repeat_this_event is False:
            # Si se pasa False, eliminamos la repetición
            evento_existente.pop('recurrence', None)

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