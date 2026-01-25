import threading
from django.core.mail import EmailMultiAlternatives
from ..plus_wrapper import Plus

def send_email_thread(subject, html_content, recipient_list):
    """ Función interna para ejecutar el envío en segundo plano """
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body="Tu cliente de correo no soporta HTML.",
            from_email="plus_recordatorios@gmail.com",
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Error asíncrono enviando email: {e}")

def send_reminder_by_email_async(appointment, customer_data, html_content):
    """ Prepara el contenido y lanza el hilo """
    user = appointment.user
    c_email = customer_data.get('email')
    
    recipient_list = [user.email]
    if c_email:
        recipient_list.append(c_email)

    subject = f"Recordatorio: {appointment.title}"
    
    # LAUNCH THREAD: This prevents the website from crashing
    thread = threading.Thread(target=send_email_thread, args=(subject, html_content, recipient_list))
    thread.start()



#----------------------------------------------------------------------------------------------------------------------------
from django.conf import settings

def get_email_change_of_time(appointment, customer_data):
    details_link = f'https://{settings.PLUS_URL}/profile_online/guest_appointment_details/{appointment.id}/'
    """ Prepare the content and start the thread """
    user = appointment.user
    doctor = user.get_full_name() or user.username
    
    # Extract customer data (dictionary prepared in the view)
    c_name = customer_data.get('name', 'Paciente')
    c_email = customer_data.get('email')
    
    recipient_list = [user.email]
    if c_email:
        recipient_list.append(c_email)

    # Date logic
    start = Plus.convert_from_utc(appointment.date_start, user.timezone)
    end = Plus.convert_from_utc(appointment.date_finish, user.timezone)

    html_content = f"""
    <html>
        <body style="font-family:Arial, sans-serif; background-color:#f4f7fb;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:12px; padding:30px;">
                <h2 style="color:#DD6B20;">Cambio en tu cita médica</h2>

                <p>Hola <strong>{c_name}</strong>,</p>

                <p>Queremos informarte que tu cita con el doctor <strong>{doctor}</strong> ha sido <strong>modificada</strong>. A continuación te compartimos los nuevos detalles:</p>

                <ul>
                    <li><strong>Motivo:</strong> {appointment.title}</li>
                    <li><strong>Nueva fecha:</strong> {start.strftime('%d/%m/%Y')}</li>
                    <li><strong>Nueva hora:</strong> {start.strftime('%H:%M')}</li>
                </ul>

                <p>Si el nuevo horario no te es conveniente, por favor contáctanos o revisa los detalles desde el siguiente enlace:</p>

                <div style="text-align:center; margin:30px 0;">
                    <a href="{details_link}" 
                    style="background:#F59E0B; color:white; padding:12px 25px; text-decoration:none; border-radius:8px;">
                    Ver detalles de la cita
                    </a>
                </div>

                <p style="font-size:14px; color:#6B7280;">
                    Gracias por tu comprensión.<br>
                    Equipo de atención
                </p>
            </div>
        </body>
    </html>
    """

    return html_content

def get_email_reminder_appoint(appointment, customer_data):
    """ Prepara el contenido y lanza el hilo """
    user = appointment.user
    doctor = user.get_full_name() or user.username
    
    # Extraer datos del cliente (diccionario preparado en la vista)
    c_name = customer_data.get('name', 'Paciente')
    c_email = customer_data.get('email')
    
    recipient_list = [user.email]
    if c_email:
        recipient_list.append(c_email)

    # Lógica de fechas (reutilizando tu objeto Plus)
    start = Plus.convert_from_utc(appointment.date_start, user.timezone)
    end = Plus.convert_from_utc(appointment.date_finish, user.timezone)
    duration_minutes = int((end - start).total_seconds() // 60)

    # Confirmation link
    from django.conf import settings
    confirm_link=f'https://{settings.PLUS_URL}/profile_online/guest_confirm_appointment/{appointment.id}/'
    html_content = f"""
    <html>
        <body style="font-family:Arial, sans-serif; background-color:#f4f7fb;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:12px; padding:30px;">
                <h2 style="color:#2B6CB0;">Recordatorio de Cita</h2>
                <p>Hola <strong>{c_name}</strong>,</p>
                <p>Tienes una cita con el doctor {doctor}:</p>
                <ul>
                    <li><strong>Motivo:</strong> {appointment.title}</li>
                    <li><strong>Hora:</strong> {start.strftime('%H:%M')}</li>
                </ul>
                <div style="text-align:center; margin:30px 0;">
                    <a href="{confirm_link}" style="background:#10B981; color:white; padding:12px 25px; text-decoration:none; border-radius:8px;">Confirmar Asistencia</a>
                </div>
            </div>
        </body>
    </html>
    """

    return html_content


from apps.profile_online.models import AppointmentOnline
from apps.agenda.models import Appointment

def send_reminder_to_the_customer(appointment, type):
    '''
    this function be use for send notifications of a appoint to his customer for whatsapp or email.
    First we will get the information of a customer if exist or of an appoint online and when get his information as email and whatsapp 
    can send the notification
    '''

    #if the proggrame send an id well we will get the information of the appoint
    if isinstance(appointment, int):
        appointment = Appointment.objects.select_related('customer').get(id=appointment)
 
    #1. here we will to create the struct of the data of the customer
    customer_data = {'name': 'Paciente', 'email': None}

    # 2. first we will see if the appointment have save a customer in his information for get his information
    if appointment.customer:
        customer_data['name'] = appointment.customer.name
        customer_data['email'] = appointment.customer.email
    elif appointment.online_appointment_id: #else now we will see if have a online appoint save
        #3. if have a <id> of a appoint online we need get the information of the customer for can send after the reminder
        try:
            online_app = AppointmentOnline.objects.get(id=appointment.online_appointment_id)
            customer_data['name'] = online_app.customer_name
            customer_data['email'] = online_app.customer_email
        except AppointmentOnline.DoesNotExist:
            return {'success': False, 'message': 'No hay datos de contacto online', 'error': 'ONLINE_DATA_MISSING'}
        

    # 4. Verify that we have an email address to send to.
    email_customer=customer_data['email']
    if not email_customer:
        return {'success': False, 'message': 'El cliente no tiene un email registrado', 'error': 'EMAIL_EMPTY'}

    # 5. get the body of the email 
    body_html=''
    if type==0:
        body_html=get_email_reminder_appoint(appointment, customer_data)
    if type==1:
        body_html=get_email_change_of_time(appointment, customer_data)

    # 6. Execute the asynchronous send (Does not block the main thread)
    send_reminder_by_email_async(appointment, customer_data, body_html)
    
    return {'success': True, 'message': f'Recordatorio enviado con éxito a {email_customer}', 'error': ''}
