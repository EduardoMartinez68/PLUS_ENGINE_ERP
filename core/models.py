from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email is obligatory')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Company(models.Model):
    name = models.CharField(max_length=300)

    class Meta:
        db_table = '"company"."company"'

    def __str__(self):
        return self.name


class Branch(models.Model):
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='id_company', related_name='branches')
    name = models.CharField(max_length=300)

    class Meta:
        db_table = '"company"."branch"'

    def __str__(self):
        return self.name
    
#------------------------------------------------------------------------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Campos obligatorios
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=600)

    # Relación con company y branch
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    id_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, db_column='id_branch')

    # Información adicional del empleado
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    hiring_date = models.DateField(blank=True, null=True)
    path_photo = models.TextField(blank=True, null=True)
    cellphone = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Admin
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    
    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
    
    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'  # Django can create this table if not exist