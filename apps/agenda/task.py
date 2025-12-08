from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from models import Appointment

@shared_task
def send_reminders():
    #get the time range for the next hour
    hour = timezone.now()
    in_one_hour = hour + timedelta(hours=1)

    # Filter only active appointments that have notifications enabled
    appointments = Appointment.objects.filter(
        date_start__range=[hour, in_one_hour],
        send_notification=True
    )

    #now we will to read all the appointments and send the emails or notification for whatsapp
    for appointment in appointments:
        # Prepare email list: main patient + guests
        recipient_list = [appointment.user.email]  #the owner of the appointment
        if appointment.emails_guests:
            recipient_list.extend(appointment.emails_guests)

        # Format message
        # here after we will to prepare the message with the preparation of the user
        mensaje = f"""
            Hola {appointment.user.get_full_name() or appointment.user.username},

            Este es un recordatorio de tu cita médica:

            Título: {appointment.title}
            Descripción: {appointment.description or 'No hay descripción'}
            Fecha de inicio: {appointment.date_start.strftime('%Y-%m-%d %H:%M')}
            Fecha de finalización: {appointment.date_finish.strftime('%Y-%m-%d %H:%M')}
            Ubicación: {appointment.location or 'No especificada'}
            Link: {appointment.link or 'No hay link'}

            Power by PLUS 🚀.
            """

        try:
            #here we will send the email
            send_mail(
                subject=f"Recordatorio: {appointment.title}",
                message=mensaje,
                from_email="tuservicio@gmail.com",
                recipient_list=recipient_list,
                fail_silently=False
            )
            enviados += 1
        except Exception as e:
            # Aquí puedes registrar errores en un log
            print(f"error to send a reminders to {appointment.id}: {e}")

    return f"{enviados} reminders sent successfully."



def send_whatsapp_text(phone_number_id, access_token, to_number_e164, text):
    """
    phone_number_id: el id 'phone_number_id' provisto por Meta para la cuenta
    access_token: token de la app/WABA (usualmente temporario o de larga duración)
    to_number_e164: '5215512345678' (con código de país, sin +)
    """
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number_e164,
        "type": "text",
        "text": {"body": text}
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()