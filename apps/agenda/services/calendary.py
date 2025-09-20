from datetime import timedelta, datetime
from django.http import JsonResponse
from ..plus_wrapper import Plus
from ..models import TypeAppoint, Appointment


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