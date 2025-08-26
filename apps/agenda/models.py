from django.db import models
from django.db import migrations, connection
#from django.contrib.auth.models import User
from django.conf import settings


def create_schema(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute('CREATE SCHEMA IF NOT EXISTS agenda;')

class TypeAppoint(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=25, default="#075EAD")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        # here we will see the type of database
        db_table = 'agenda.type_appoint'

    def __str__(self):
        return self.name

class Appointment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    date_start = models.DateTimeField(auto_now_add=True)
    date_finish = models.DateTimeField(auto_now_add=True)

    time_alert = models.IntegerField(default=0) #this is for know when to alert in minute
    priority = models.SmallIntegerField(default=0)
    activate_event_all_the_day = models.BooleanField(default=False)


    emails_guests = models.JSONField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)

    repeat_this_event = models.BooleanField(default=False)
    time_repeat = models.SmallIntegerField(default=0) #this is for that the ERP knows how often to repeat this event in days
    finish_repeat_date = models.DateTimeField(null=True, blank=True, help_text="This is for that the ERP knows when to stop repeating this event")


    send_notification = models.BooleanField(default=True)
    i_am_free = models.BooleanField(default=True)
    
    id_type_appoint = models.ForeignKey(TypeAppoint, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'agenda.appointments'

    def __str__(self):
        return self.title


class Settings(models.Model):
    email_alert = models.TextField()
    time_alert = models.IntegerField(default=0)
    send_notification = models.BooleanField(default=True)
    default_type_appoint = models.ForeignKey(TypeAppoint, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'agenda.settings'

    def __str__(self):
        return self.email_alert
    
