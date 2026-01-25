from django.db import models
from django.db import migrations, connection
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from apps.customers.models import Customer

#from django.contrib.auth.models import User
from django.conf import settings

class TypeAppoint(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=25, default="#075EAD")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        # here we will see the type of database
        db_table = 'agenda_type_appoint'

    def __str__(self):
        return self.name

class Appointment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    date_start = models.DateTimeField()
    date_finish = models.DateTimeField()

    time_alert = models.IntegerField(default=0) #this is for know when to alert in minute
    priority = models.SmallIntegerField(default=0)
    activate_event_all_the_day = models.BooleanField(default=False)


    emails_guests = models.JSONField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    id_event_in_google_calendar=models.TextField(null=True, unique=True, db_index=True)

    repeat_this_event = models.BooleanField(default=False)
    time_repeat = models.SmallIntegerField(default=0) #this is for that the ERP knows how often to repeat this event in days
    finish_repeat_date = models.DateTimeField(null=True, blank=True, help_text="This is for that the ERP knows when to stop repeating this event")


    send_notification = models.BooleanField(default=True)
    i_am_free = models.BooleanField(default=True)
    
    id_type_appoint = models.ForeignKey(TypeAppoint, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, db_column='customer') #this is for send reminders by email and whatsapp
    reminder_sent = models.BooleanField(default=False, db_index=True)

    #this is for know if this appoint was save in the profile online. This is for get his data after
    online_appointment_id = models.IntegerField(null=True, blank=True, help_text="Online appointment ID")
    
    #character of the Appointment 
    PENDING = 'P'
    CONFIRMED = 'C'
    CANCELLED = 'X'
    COMPLETED = 'A'  # 'A' of attended
    NO_SHOW = 'N'    # the customer not arrive
    STATUS_CHOICES = [
        (PENDING, 'agenda.status.pending'),     # Por confirmar
        (CONFIRMED, 'agenda.status.confirmed'), # Confirmada por el paciente
        (CANCELLED, 'agenda.status.cancelled'), # Cancelada previamente
        (COMPLETED, 'agenda.status.attended'),  # El paciente ya entró y salió
        (NO_SHOW, 'agenda.status.no_show'),     # El paciente no vino (ausente)
    ]
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True # this is for filter more fast
    )


    class Meta:
        db_table = 'agenda_appointments'

    def __str__(self):
        return self.title

class Settings(models.Model):
    email_alert = models.TextField()
    time_alert = models.IntegerField(default=0)
    send_notification = models.BooleanField(default=True)
    default_type_appoint = models.ForeignKey(TypeAppoint, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'agenda_settings'

    def __str__(self):
        return self.email_alert
    
class GoogleToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = EncryptedTextField()
    refresh_token = EncryptedTextField()
    token_uri = EncryptedTextField()
    client_id = EncryptedTextField()
    client_secret = EncryptedTextField()
    scopes = EncryptedTextField()