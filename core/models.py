from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    path_photo = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=600)
    email = models.EmailField(unique=True)
    id_company = models.BigIntegerField(blank=True, null=True)
    id_branch = models.BigIntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return self.email
    

    class Meta:
            db_table = 'users' 



class Company(models.Model):
    name = models.CharField(max_length=300)

    class Meta:
        db_table = '"company"."company"'

    def __str__(self):
        return self.name


class Branch(models.Model):
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='id_company', related_name='branches')

    class Meta:
        db_table = '"company"."branch"'

    def __str__(self):
        return f'Branch {self.id} - Company {self.id_company_id}'