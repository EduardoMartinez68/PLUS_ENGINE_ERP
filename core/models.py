from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models



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
    company_name = models.CharField(max_length=300, null=True)
    name_of_the_person_in_charge = models.CharField(max_length=150)
    email_of_the_person_in_charge = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company"."company'

    def __str__(self):
        return self.company_name or f"Company {self.id}"

class Branch(models.Model):
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    #information of the branch
    name_branch = models.CharField(max_length=500)
    nickname = models.CharField(max_length=100, null=True)
    email_branch = models.TextField(null=True)
    name_of_the_person_in_charge = models.TextField(null=True)
    email_of_the_person_in_charge = models.TextField(null=True)
    country = models.CharField(max_length=2, null=True)
    address = models.TextField(null=True)
    postal_code = models.CharField(max_length=10, null=True)

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

    #information creation
    creation_date = models.DateField(auto_now_add=True)
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = 'company"."branch'

    def __str__(self):
        return self.name_branch
    
class UserType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = 'company"."user_type'

    def __str__(self):
        return self.name
    
class Permit(models.Model):
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=True)
    view_permits = models.BooleanField(default=True)
    edit_permits = models.BooleanField(default=True)
    delete_permits = models.BooleanField(default=True)

    class Meta:
        db_table = 'company"."permits'

    def __str__(self):
        return self.name

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
        db_table = 'company"."setting'

    def __str__(self):
        return f"Settings {self.id}"






#----------------------------------------------------THIS IS FOR CREATE THE TABLE USER OF THE ERP--------------------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Required fields
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=600)

    # Relationship with company and branch
    id_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, db_column='id_company')
    id_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, db_column='id_branch')

    # Additional employee information
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    hiring_date = models.DateField(blank=True, null=True)
    path_photo = models.TextField(blank=True, null=True)
    cellphone = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, default='America/Mexico_City')

    # Required fields
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