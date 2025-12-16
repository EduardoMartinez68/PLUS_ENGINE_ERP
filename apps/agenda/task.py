from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from models import Appointment
from core.models import WhatsAppAccount
import re

def send_reminder_by_email(appointment):
    from django.core.mail import EmailMultiAlternatives

    recipient_list = [appointment.user.email]
    if appointment.emails_guests:
        recipient_list.extend(appointment.emails_guests)

    paciente = appointment.user.get_full_name() or appointment.user.username

    html_content = f"""
    <html>
    <body style="margin:0; padding:0; background-color:#f4f7fb; font-family:Arial, sans-serif;">
        
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f7fb; padding: 30px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 10px rgba(0,0,0,0.08);">
                        
                        <!-- HEADER -->
                        <tr>
                            <td style="background:#2B6CB0; padding:25px; text-align:center; color:white; font-size:28px; font-weight:bold;">
                                Recordatorio de tu Cita Médica
                            </td>
                        </tr>

                        <!-- CONTENIDO PRINCIPAL -->
                        <tr>
                            <td style="padding: 30px; color:#333333; font-size:16px; line-height:1.6;">
                                
                                <p style="font-size:18px; margin-bottom:20px;">
                                    👋 Hola <strong>{paciente}</strong>,
                                </p>

                                <p style="margin-bottom:15px;">
                                    Este es un recordatorio de tu próxima cita médica.  
                                    Aquí tienes los detalles de tu consulta:
                                </p>

                                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px; background:#f4f7fb; border-radius:8px; padding:20px;">
                                    <tr>
                                        <td style="font-size:14px; color:#666;">
                                            <strong style="color:#333;">Motivo:</strong> {appointment.title}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding-top:10px; font-size:14px; color:#666;">
                                            <strong style="color:#333;">Fecha:</strong> {appointment.date_start.strftime('%Y-%m-%d %H:%M')}
                                            <br>
                                            <strong style="color:#333;">Duración:</strong> {appointment.date_start.strftime('%H:%M')} – {appointment.date_finish.strftime('%H:%M')}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding-top:10px; font-size:14px; color:#666;">
                                            <strong style="color:#333;">Ubicación:</strong> {appointment.location or 'No especificado'}
                                        </td>
                                    </tr>
                                    {'<tr><td style="padding-top:10px; font-size:14px; color:#666;"><strong style="color:#333;">Descripción:</strong> ' + appointment.description + '</td></tr>' if appointment.description else ''}
                                    {'<tr><td style="padding-top:10px; font-size:14px; color:#666;"><strong style="color:#333;">Link:</strong> <a href="' + appointment.link + '" style="color:#4a90e2;">Abrir enlace</a></td></tr>' if appointment.link else ''}
                                </table>

                                <p style="margin-top:25px;">
                                    Si necesitas modificar o cancelar tu cita, puedes hacerlo desde tu panel de paciente.
                                </p>

                                <p style="margin-top:30px; font-size:13px; color:#999;">
                                    Atentamente,<br>
                                    <strong>Equipo {user.branch.name_branch}</strong>
                                </p>

                            </td>
                        </tr>

                        <!-- FOOTER -->
                        <tr>
                            <td style="background:#f0f3f8; padding:15px; text-align:center; font-size:12px; color:#777;">
                                Este es un mensaje automático, por favor no respondas este correo.<br><br>
                                <a href="softwarclinico.online">Power by PLUS 🚀 Sistema Clínico Profesional</a>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    subject = f"Recordatorio de tu cita: {appointment.title}"

    email = EmailMultiAlternatives(
        subject=subject,
        body="Tu cliente de correo no soporta HTML, pero tienes una cita pendiente.",
        from_email="tuservicio@gmail.com",
        to=recipient_list
    )

    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
    except Exception as e:
        print(f"Error to send this email {appointment.id}: {e}")

def send_whatsapp_text(phone_number_id, access_token, to_number_e164, text):
    """
    phone_number_id: el id 'phone_number_id' provisto por Meta para la cuenta
    access_token: token de la app/WABA (usualmente temporario o de larga duración)
    to_number_e164: '5215512345678' (con código de país, sin +)
    """
    import requests
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

def this_cellphone_is_valid(cellphone):
    """
    Validates whether a number is accepted by WhatsApp according to the E.164 format.
    Returns True if the number is valid, False otherwise.
    """
    if not cellphone:
        return False

    # Clean spaces and scripts
    cleaned = re.sub(r"[ \-\(\)]", "", cellphone)

    # It must start with +
    if not cleaned.startswith("+"):
        return False

    # It must conform to the E.164 format: +, then 8 to 15 digits
    pattern = r"^\+[1-9]\d{7,14}$"

    return bool(re.match(pattern, cleaned))

def get_account(company, branch):
    """
    Returns the WhatsApp account associated with the company and branch.

    If it doesn't exist or an error occurs, returns None.
    """
    try:
        return WhatsAppAccount.objects.filter(company=company, branch=branch).first()
    except Exception:
        return None
        
def send_reminder_by_whatsapp(appointment):
    #first we will see if the appointment have a customer 
    customer=appointment.customer
    if customer:
        #if have a customer now we will see if this customer have a cellphone
        cellphone=customer.cellphone
        if this_cellphone_is_valid(cellphone):
            #now we will get the key of API of whatsapp of the user from the database if exist 
            company=appointment.user.company
            branch=appointment.user.branch
            whatsapp_account=get_account(company, branch)

            if whatsapp_account:
                #if have a cellphone for send a message and get the key of the API of the user of whatsapp to we will try send the message
                mensaje = f""" 
                👋 Hola {appointment.user.get_full_name() or appointment.user.username}, 
                Este es un recordatorio de tu cita médica: {appointment.title} 
                📅 {appointment.date_start.strftime('%Y-%m-%d %H:%M')}--{appointment.date_finish.strftime('%Y-%m-%d %H:%M')} 

                
                {appointment.description or ''} 📍 {appointment.location or ''} 
                Link: {appointment.link or ''} 
                
                Power by PLUS 🚀 Sistema Clínico Profesional. 
                https://softwarclinico.online
                """
                send_whatsapp_text(whatsapp_account.phone_number_id, whatsapp_account.access_token, cellphone, mensaje)




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
        send_reminder_by_email(appointment)
        send_reminder_by_whatsapp(appointment)
        

    return f"reminders sent successfully."


def renovar_limites_mensuales():
    pass 