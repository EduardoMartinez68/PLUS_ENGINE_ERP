from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from apps.agenda.plus_wrapper import Plus
from models import Appointment
from core.models import WhatsAppAccount, UserSubscription
import re
from django.db.models import F
from django.core.cache import cache

def send_reminder_by_email(appointment):
    try:
        from django.core.mail import EmailMultiAlternatives


        recipient_list = [appointment.user.email]

        #here save the email of the customer 
        if appointment.customer.email:
            recipient_list.append(appointment.customer.email)

        #if this event have guests, we will to add to the recipient list
        if appointment.emails_guests:
            # convertir a lista si es string
            if isinstance(appointment.emails_guests, str):
                import ast
                try:
                    guests = ast.literal_eval(appointment.emails_guests)
                except Exception:
                    guests = []
            else:
                guests = appointment.emails_guests

            # filtrar solo strings válidos
            guests = [g for g in guests if isinstance(g, str) and g.strip()]
            recipient_list.extend(guests)
        
        doctor = appointment.user.get_full_name() or appointment.user.username
        customer = appointment.customer.name if appointment.customer else "Paciente"
        user = appointment.user

        #here we will see the time of the appoint
        timezone_user=user.timezone
        start = Plus.convert_from_utc(appointment.date_start, timezone_user)
        end = Plus.convert_from_utc(appointment.date_finish, timezone_user)
        duration: timedelta = end - start
        duration_minutes = int(duration.total_seconds() // 60) # Duration in minutes

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
                                        👋 Hola <strong>{customer}</strong>,
                                    </p>

                                    <p style="margin-bottom:15px;">
                                        Este es un recordatorio de tu próxima cita médica con el doctor {doctor}.  
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
                                                <strong style="color:#333;">Fecha:</strong> {Plus.convert_from_utc(appointment.date_start,user.timezone).strftime('%d/%m/%Y')}
                                                <br>
                                                <strong style="color:#333;">Duración:</strong> {duration_minutes} minutos
                                                <br>
                                                <strong style="color:#333;">Hora:</strong> {start.strftime('%H:%M')} – {end.strftime('%H:%M')}
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
                                    <a href="denty.cloud">Power by PLUS Denty.Cloud</a>
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
            from_email="plus_recordatorios@gmail.com",
            to=recipient_list,
        )

        email.attach_alternative(html_content, "text/html")
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

    Here we will to save in cache the account for not do many queries to the database
    """
    key = f"wa_acc_{company.id}_{branch.id}"
    whatsapp_account = cache.get(key)
    
    if not whatsapp_account:
        whatsapp_account = WhatsAppAccount.objects.filter(company=company, branch=branch).first()
        # save in for 10 minutes for that the sub-task can read
        cache.set(key, whatsapp_account, 600) 
        
    return whatsapp_account
        
def send_reminder_by_whatsapp(appointment, whatsapp_account):
    customer = appointment.customer
    cellphone = customer.cellphone
    
    # Aquí corregí un detalle: El saludo debe ser al PACIENTE (customer), no al dentista (user)
    nombre_paciente = customer.get_full_name() or "Paciente"
        
    mensaje = f"""👋 Hola {nombre_paciente},
    Este es un recordatorio de tu cita médica: *{appointment.title}*
    📅 {appointment.date_start.strftime('%d/%m/%Y %H:%M')}

    📍 {appointment.location or 'Consultorio'}
    {f'🔗 Link: {appointment.link}' if appointment.link else ''}

    Power by PLUS 🚀
    """

    
    # Usamos los datos del 'account' que ya recibimos por parámetro
    send_whatsapp_text(
        whatsapp_account.phone_number_id, 
        whatsapp_account.access_token, 
        cellphone, 
        mensaje
    )




@shared_task
def send_reminders():
    # 1. We use select_related to retrieve the user's data all at once (avoids N+1)
    # 2. We only look for quotes that have NOT been submitted
    now = timezone.now()
    in_one_hour = now + timedelta(hours=1)
    
    appointment_ids = Appointment.objects.filter(
        date_start__range=[now, in_one_hour],
        send_notification=True,
        reminder_sent=False
    ).values_list('id', flat=True)

    for appointment_id in appointment_ids:
        # We launch individual subtasks.
        # If one fails, it doesn't stop the others.
        send_individual_appointment_notifications.delay(appointment_id)

    # Mark as sent immediately so the next execution (in 5 min) won't take it
    Appointment.objects.filter(id__in=appointment_ids).update(reminder_sent=True)

    return f"{len(appointment_ids)} appoints send."


@shared_task(bind=True, max_retries=3)
def send_individual_appointment_notifications(self, appointment_id):
    try:
        #here we will get the appointment with all the related data that we need
        appointment = Appointment.objects.select_related(
            'user__branch', 'user__company', 'customer'
        ).get(id=appointment_id)
        
        #we will see if exist customer and if the customer have cellphone
        customer = appointment.customer
        if not customer:
            return
        
        #now for send a message for whatsapp we will if this customer have a phone
        if customer.cellphone and this_cellphone_is_valid(customer.cellphone):
            # 1. Access the account and validate the balance
            acc = get_account(appointment.user.company, appointment.user.branch) #now we will get the key of API of whatsapp of the user from the database if exist 
            if acc:
                #if exist a account for send whatsapp messages, now we will see if the user can send more messages this month
                sub=UserSubscription.objects.filter(user=appointment.user).first()
                if not sub:
                    return
                
                if not sub.can_send_message():
                    return
                
                #send whatsapp reminder
                send_reminder_by_whatsapp(appointment, acc)
                acc.messages_sent_this_month = F('messages_sent_this_month') + 1 #INCREMENT THE COUNTER OF WHATSAPP MESSAGES SENT THIS MONTH
                acc.save(update_fields=['messages_sent_this_month'])

        #we will see if the customer have a email for send the message
        if customer.email:
            #send email reminder
            send_reminder_by_email(appointment)


    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


# apps.agenda.tasks.py
@shared_task
def renovar_limites_mensuales():
    # The .update() method translates to a single line of SQL:
    # UPDATE core_whatsappaccount SET messages_sent_this_month = 0;
    # This is instantane even with many records.
    WhatsAppAccount.objects.all().update(messages_sent_this_month=0)
    return "Límites mensuales reiniciados."