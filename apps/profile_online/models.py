
#-----------------------------------------------------------------------------PROFILES AND STORE ONLINES---------------------------------------------------
from core.models import CustomUser
from django.db import models
import hashlib
import os
import uuid
from io import BytesIO
from django.db import models
from PIL import Image

class PublicProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="public_profile"
    )

    #profile URL
    public_slug = models.SlugField(
        unique=True,
        max_length=100,
        null=True,
        blank=True
    )

    #this is for know if the profile can show in the web
    is_public=models.BooleanField(
        default=True,
        null=True,
        blank=True
    )
    is_verified = models.BooleanField(default=False)

    title = models.CharField(max_length=255)  # example: Dra. Mariana Santiago
    specialty = models.CharField(max_length=255)
    university = models.CharField(max_length=255, blank=True, null=True)

    about = models.TextField(blank=True, null=True)

    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    cover_image = models.ImageField(upload_to="profiles/covers/", blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/avatar/", blank=True, null=True)

    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_public"]),
        ]

    def __str__(self):
        return self.title
    

class ProfileService(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="services"
    )

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="MXN")

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"
    

class ProfileSchedule(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    day_of_week = models.PositiveSmallIntegerField(
        choices=[
            (1, "Lunes"),
            (2, "Martes"),
            (3, "Miercoles"),
            (4, "Jueves"),
            (5, "Viernes"),
            (6, "Sabado"),
            (7, "Domingo"),
        ]
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]


class ProfileLocation(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="locations"
    )

    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    google_maps_url = models.URLField(blank=True, null=True)
    is_main = models.BooleanField(default=False)


class ProfileReview(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    author_name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()

    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]#here you can create the body of the database 

#-----------------------------------------

class ScheduleOnline(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="schedules_online"
    )

    DAY_CHOICES = (
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    )

    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    slot_duration = models.PositiveIntegerField(
        default=30,
        help_text="Duración de cada cita en minutos"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.profile} - {self.get_day_of_week_display()}"
    
class ScheduleException(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="schedule_exceptions"
    )

    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.profile} - {self.date}"
    
class AppointmentOnline(models.Model):
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="online_appointment"
    )
    
    #-------------information of the customer-------------
    customer_name=models.CharField(max_length=150, null=False)
    customer_email=models.CharField(max_length=150, null=False)
    customer_phone=models.CharField(max_length=150, null=True)
    patient_whatsapp = models.CharField(max_length=20,blank=True)

    #-------------information of the appoint--------------
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    #---------------information about the appoint------------------
    notes = models.TextField(blank=True)
    service = models.ForeignKey(
        ProfileService,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )