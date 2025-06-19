# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Casos(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casos'


class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_branch = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=300)
    email = models.TextField(blank=True, null=True)
    this_customer_is_a_company = models.BooleanField()
    company_name = models.CharField(max_length=255, blank=True, null=True)
    rfc = models.CharField(max_length=50, blank=True, null=True)
    curp = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    cellphone = models.CharField(max_length=50, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField()
    country = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'customer'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocumentosRelacionados(models.Model):
    caso = models.ForeignKey(Casos, models.DO_NOTHING)
    titulo = models.CharField(max_length=255)
    contenido = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documentos_relacionados'


class Permisos(models.Model):
    clave = models.TextField(unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permisos'


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    path_photo = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=600)
    email = models.CharField(unique=True, max_length=254)
    password = models.CharField(max_length=128)
    id_company = models.BigIntegerField(blank=True, null=True)
    id_branch = models.BigIntegerField(blank=True, null=True)
    is_active = models.BooleanField()
    is_staff = models.BooleanField()
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'
