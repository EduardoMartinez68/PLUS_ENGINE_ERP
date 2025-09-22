from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import hashlib
import os
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from PIL import Image
from cryptography.fernet import Fernet


key = os.getenv("DATA_ENCRYPTION_KEY")
cipher = Fernet(key.encode())

# helper: calcular hash (SHA-256) para email (normalizar a minúsculas)
def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()

def encrypt_field(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.encode("utf-8")
    return cipher.encrypt(value)

def decrypt_field(value):
    if value is None:
        return None
    try:
        return cipher.decrypt(value).decode("utf-8")
    except Exception:
        return None

def user_avatar_path(instance, filename):
    # instance.company.id, instance.branch.id
    ext = filename.split('.')[-1]
    return f"users/company_{instance.company.id}/branch_{instance.branch.id}/{uuid.uuid4().hex}_avatar.{ext}"

def logo_path(instance, filename):
    # instance.company.id, instance.branch.id
    ext = filename.split('.')[-1]
    return f"users/company_{instance.company.id}/branch_{instance.branch.id}/{uuid.uuid4().hex}_logo.{ext}"

def logo_company(instance, filename):
    # instance.company.id, instance.branch.id
    ext = filename.split('.')[-1]
    return f"users/company_{instance.company.id}/{uuid.uuid4().hex}_logo.{ext}"

#-----------------------------------------------------THIS IS FOR CREATE THE SKELETON OF THE ERP-------------------------------------------------------
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
    # Basic information
    logo = models.ImageField(upload_to=logo_company, blank=True, null=True)
    company_name = models.CharField(max_length=300, null=True)
    name_of_the_person_in_charge = models.CharField(max_length=150)
    email_of_the_person_in_charge = models.TextField()
    creation_date = models.DateField(auto_now_add=True)

    # Contact information
    phone = models.CharField(max_length=25, blank=True, null=True)
    cellphone = models.CharField(max_length=25, blank=True, null=True)
    support_email = models.EmailField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    # address
    address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)  # MX, PL, etc
    timezone = models.CharField(max_length=50, default="America/Mexico_City")

    # Sensitive data encrypted
    _tax_id = models.BinaryField(db_column="tax_id", blank=True, null=True)
    _bank_account = models.BinaryField(db_column="bank_account", blank=True, null=True)
    bank_name = models.CharField(max_length=150, blank=True, null=True)
    _google_password = models.BinaryField(db_column="google_password", blank=True, null=True)
    google_user = models.TextField(blank=True, null=True)

    # Internal configuration
    default_currency = models.CharField(max_length=5, default="MXN")
    decimal_separator = models.CharField(max_length=1, default=".")
    thousands_separator = models.CharField(max_length=1, default=",")
    date_format = models.CharField(max_length=20, default="DD/MM/YYYY")
    activated = models.BooleanField(default=True)

    # Audit
    created_by = models.CharField(max_length=150, blank=True, null=True)
    updated_by = models.CharField(max_length=150, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "companies_company"

    def __str__(self):
        return self.company_name or f"Company {self.id}"

    # Getters and setters for encrypted fields
    @property
    def tax_id(self):
        return decrypt_field(self._tax_id)

    @tax_id.setter
    def tax_id(self, value):
        self._tax_id = encrypt_field(value)

    @property
    def bank_account(self):
        return decrypt_field(self._bank_account)

    @bank_account.setter
    def bank_account(self, value):
        self._bank_account = encrypt_field(value)

    @property
    def google_password(self):
        return decrypt_field(self._google_password)

    @google_password.setter
    def google_password(self, value):
        self._google_password = encrypt_field(value)

    # Logo validation and optimization
    def save(self, *args, **kwargs):
        MAX_SIZE_MB = 5
        if self.logo and self.logo.size > MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"Logo cannot exceed {MAX_SIZE_MB} MB")

        if self.logo:
            try:
                img = Image.open(self.logo)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                max_size = (800, 800)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)
                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=85)
                    buffer.seek(0)
                    self.logo.save(f"{uuid.uuid4().hex}.webp", ContentFile(buffer.read()), save=False)
            except Exception:
                pass

        super().save(*args, **kwargs)

class Branch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='company')

    #information of the branch
    logo = models.ImageField(upload_to=logo_path, blank=True, null=True)
    name_branch = models.CharField(max_length=500)
    nickname = models.CharField(max_length=100, null=True)
    email_branch = models.TextField(null=True)
    name_of_the_person_in_charge = models.TextField(null=True)
    email_of_the_person_in_charge = models.TextField(null=True)
    country = models.CharField(max_length=2, null=True) #mx, pl , etc
    address = models.TextField(null=True)
    postal_code = models.CharField(max_length=10, null=True)
    timezone = models.CharField(max_length=50, default="America/Mexico_City")

    #contact information
    cellphone = models.CharField(max_length=25, null=True)
    phone = models.CharField(max_length=25, null=True)
    support_email = models.EmailField(blank=True, null=True)
    notification_email = models.EmailField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.TextField(null=True)

    #-----Google Information-----
    user_google = models.TextField(null=True)
    password_google = models.TextField(null=True)

    # Additional useful fields
    _bank_account = models.BinaryField(db_column="bank_account", blank=True, null=True)
    default_currency = models.CharField(max_length=5, default="MXN")  
    default_language = models.CharField(max_length=10, default="es") 
    opening_time = models.TimeField(blank=True, null=True) 
    closing_time = models.TimeField(blank=True, null=True) 
    opening_days = models.CharField(max_length=7, default='0111110')  #Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday

    enable_online_orders = models.BooleanField(default=False)  # Allow online orders. This is for if the user need use API like PLUS SHOP
    notes = models.TextField(blank=True, null=True) 
    last_audit_date = models.DateField(blank=True, null=True)  # Date of last audit or review


    #information creation
    creation_date = models.DateField(auto_now_add=True)
    activated = models.BooleanField(default=True)

    @property
    def bank_account(self):
        val = self._bank_account
        if val:
            try:
                return cipher.decrypt(val).decode()
            except Exception:
                return None
        return None

    @bank_account.setter
    def bank_account(self, value):
        if value is None:
            self._bank_account = None
        else:
            self._bank_account = cipher.encrypt(value.encode())

    class Meta:
        db_table = "companies_branch"

    def __str__(self):
        return self.name_branch

class UserDepartment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = "companies_user_type"

    def __str__(self):
        return self.name
    
#----------------------------------------------------this is for create the roles and permissions of the ERP------------------------------------------------
#here table is for save all the permissions that exist in all the apps of the ERP. This permits be load when the server is started
class Permit(models.Model):
    code = models.CharField(max_length=150, unique=True)  # example "add_product"
    app = models.CharField(max_length=50)  # example "inventory"
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.app}: {self.code}"
    
#this model is the roles that exist in the company. Each role have a relation with the table <PermissionTable> for know all the permits that have this role
class UserRole(models.Model):
    #information of the rol of the user
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=True)

    class Meta:
        unique_together = ('id_company', 'name')
        db_table = 'companies_roles'


    def __str__(self):
        return self.name
    
#here is for save all the permits of the ERP in a company of the user and his status. This is table is for after assign to a rol in the company and save in the users
class Role(models.Model):
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, null=False)

    class Meta:
        unique_together = ('role', 'permit')



#----------------------------------------------------THIS IS FOR CREATE THE TABLE SETTINGS OF THE ERP--------------------------------------------------------
class Setting(models.Model):
    company_color = models.CharField(max_length=7, default="#075FAF")
    secondary_color = models.CharField(max_length=7, default="#074c8dff")
    button_color = models.CharField(max_length=7, default="#075FAF")
    button_success = models.CharField(max_length=7, default="#075FAF")
    currency_type = models.CharField(max_length=5, default="MXN")
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    font_family = models.CharField(max_length=100, default="Inter")

    #config facture 
    currency_symbol = models.CharField(max_length=5, default="$")
    decimal_separator = models.CharField(max_length=1, default=".")
    thousands_separator = models.CharField(max_length=1, default=",")
    currency_position = models.CharField(max_length=10, choices=[('before', 'Antes del número'), ('after', 'Después del número')], default='before')

    #config location
    language = models.CharField(max_length=10, default="es")
    timezone = models.CharField(max_length=50, default="America/Mexico_City")
    date_format = models.CharField(max_length=20, default="DD/MM/YYYY")

    class Meta:
        db_table = 'companies_setting'

    def __str__(self):
        return f"Settings {self.id}"






#----------------------------------------------------THIS IS FOR CREATE THE TABLE USER OF THE ERP--------------------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Required fields
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)
    _name = models.BinaryField(db_column="name", blank=True, null=True)
    email_hash = models.CharField(max_length=64, unique=True, db_index=True)
    _email = models.BinaryField(db_column="email", blank=True, null=True)
    username = models.CharField(max_length=600)

    # Relationship with company and branch
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, db_column='id_branch')
    user_role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, db_column='id_user_role')
    user_department = models.ForeignKey(UserDepartment, on_delete=models.SET_NULL, null=True, db_column='id_user_department')

    # Additional employee information
    _address = models.BinaryField(db_column="address", blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    _date_of_birth = models.BinaryField(db_column="date_of_birth", blank=True, null=True)  # iso string encrypted
    hiring_date = models.DateField(blank=True, null=True)
    _cellphone = models.BinaryField(db_column="cellphone", blank=True, null=True)
    _phone = models.BinaryField(db_column="phone", blank=True, null=True)

    #options ubication 
    timezone = models.CharField(max_length=50, blank=True, default='America/Mexico_City')
    language =  models.CharField( max_length=10, blank=True, default='es')

    # Required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Admin
    USERNAME_FIELD = 'email_hash' #in the login your need calculate the has 
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
    
    # ----------------- helpers de cifrado -----------------
    def _get_field(self, name: str):
        val = getattr(self, f"_{name}")
        if val:
            try:
                return cipher.decrypt(val).decode("utf-8")
            except Exception:
                return None
        return None

    def _set_field(self, name: str, value):
        if value is None:
            setattr(self, f"_{name}", None)
        else:
            if not isinstance(value, (str, bytes)):
                value = str(value)
            if isinstance(value, str):
                value = value.encode("utf-8")
            setattr(self, f"_{name}", cipher.encrypt(value))

    # ----------------- properties públicas -----------------
    @property
    def email(self):
        return self._get_field("email")

    @email.setter
    def email(self, value):
        if value:
            # almacenar hash para búsquedas/autenticación
            self.email_hash = sha256_hex(value)
            self._set_field("email", value)
        else:
            self._set_field("email", None)
            self.email_hash = None

    @property
    def name(self):
        return self._get_field("name")

    @name.setter
    def name(self, value):
        self._set_field("name", value)

    @property
    def address(self):
        return self._get_field("address")

    @address.setter
    def address(self, value):
        self._set_field("address", value)

    @property
    def cellphone(self):
        return self._get_field("cellphone")

    @cellphone.setter
    def cellphone(self, value):
        self._set_field("cellphone", value)

    @property
    def phone(self):
        return self._get_field("phone")

    @phone.setter
    def phone(self, value):
        self._set_field("phone", value)

    @property
    def date_of_birth(self):
        # almacenamos la fecha como ISO string en _date_of_birth (encrypted)
        val = self._get_field("date_of_birth")
        return val  # devuelves string ISO; conviente parsearlo fuera

    @date_of_birth.setter
    def date_of_birth(self, value):
        # acepta date o string
        if value is None:
            self._set_field("date_of_birth", None)
        else:
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            self._set_field("date_of_birth", value)

    # ----------------- save (avatar validations) -----------------
    def save(self, *args, **kwargs):
        MAX_SIZE_MB = 5
        if self.avatar and self.avatar.size > MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"Avatar cannot exceed {MAX_SIZE_MB} MB")

        if self.avatar:
            # optimize avatar similar to Customer.save
            try:
                img = Image.open(self.avatar)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                max_size = (800, 800)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)
                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=85)
                    buffer.seek(0)
                    self.avatar.save(f"{uuid.uuid4().hex}.webp", ContentFile(buffer.read()), save=False)
            except Exception:
                # If optimization fails, continue and let save resolve if there is an error
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.email_hash
    
