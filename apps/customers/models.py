from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import uuid

#here load the key of encrypt for encrypt the information of the customer
from cryptography.fernet import Fernet
import os
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField

key = os.getenv("DATA_ENCRYPTION_KEY")
cipher = Fernet(key.encode())

class CustomerSource(models.Model):
    """
    Customer source (how they contacted us or who referred them).
    Example: Website, referral, Facebook ad, trade show, e-commerce platform.
    """
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="customer_sources", null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "customers_customer_source"
        verbose_name = "Customer Source"
        verbose_name_plural = "Customer Sources"
        unique_together = ("company", "name") #this is for that not exist type repeat in the company 

    def __str__(self):
        return self.name
    
class CustomerType(models.Model):
    """
    Type or category of customer. 
    Example: Customer, Supplier, Distributor, Patient, Student.
    """
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="customer_types", null=True, blank=True)
    color = models.CharField(max_length=7, default="#3498db",help_text="Hex color code, e.g., #3498db",  null=False)
    name = models.CharField(max_length=50, unique=True, null=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "customers_customer_type"
        verbose_name = "Customer Type"
        verbose_name_plural = "Customer Types"
        unique_together = ("company", "name") #this is for that not exist type repeat in the company 

    def __str__(self):
        return self.name
    

# upload_to dinamic
def customer_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"customers/{uuid.uuid4().hex}_avatar.{ext}"

class Customer(models.Model):
    #------personal information------
    id = models.BigAutoField(primary_key=True)  
    avatar = models.ImageField(upload_to=customer_avatar_path, blank=True, null=True)
    sku= models.CharField(db_column="sku", blank=True, null=True, max_length=300)
    name=EncryptedCharField(db_column="name", blank=True, null=True, max_length=300)
    email = EncryptedCharField(db_column="email", blank=True, null=True, max_length=300)
    phone = EncryptedCharField(db_column="phone", blank=True, null=True, max_length=20)
    cellphone = EncryptedCharField(db_column="cellphone", blank=True, null=True, max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)

    GENDER_CHOICES = [
        ("M", "Men"),
        ("F", "Woman"),
        ("O", "Other"),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        db_column="gender"
    )

    #------information of address------
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO code (ej: MX, US)
    address=EncryptedCharField(db_column="address", blank=True, null=True, max_length=800)
    city=EncryptedCharField(db_column="city", blank=True, null=True, max_length=500)
    state=EncryptedCharField(db_column="state", blank=True, null=True, max_length=500)
    postal_code=EncryptedCharField(db_column="postal_code", blank=True, null=True, max_length=10)
    num_ext=EncryptedCharField(db_column="num_ext", blank=True, null=True, max_length=5)
    num_int=EncryptedCharField(db_column="num_int", blank=True, null=True, max_length=5)
    reference=EncryptedCharField(db_column="reference", blank=True, null=True, max_length=500)

    #--information of the company------
    this_customer_is_a_company = models.BooleanField(default=False)
    company_name=EncryptedCharField(db_column="company_name", blank=True, null=True, max_length=500)
    contact_name=EncryptedCharField(db_column="contact_name", blank=True, null=True, max_length=300)
    contact_email=EncryptedCharField(db_column="contact_email", blank=True, null=True, max_length=300)
    contact_cellphone = EncryptedCharField(db_column="contact_cellphone", blank=True, null=True, max_length=20)
    contact_phone = EncryptedCharField(db_column="contact_phone", blank=True, null=True, max_length=20)
    website = EncryptedCharField(db_column="website", blank=True, null=True, max_length=500)
    note = models.TextField(blank=True, null=True)

    #--information of the customer in the company------
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="customers", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="customers", null=True, blank=True)
    points = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    customer_type = models.ForeignKey(
            "CustomerType", on_delete=models.SET_NULL, null=True, blank=True
        )
    source = models.ForeignKey(
        "CustomerSource", on_delete=models.SET_NULL, null=True, blank=True
    ) #how get this customer, google, facebook, ads, etc
    priority = models.SmallIntegerField(default=0)
    number_of_price_of_sale = models.SmallIntegerField(default=1)

    creation_date = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = "customers_customer"
        indexes = [
            models.Index(fields=["company"], name="idx_customer_company"),
            models.Index(fields=["activated"], name="idx_customer_activated"),
        ]

    def save(self, *args, **kwargs):
        MAX_SIZE_MB = 5

        #here we will to limit the size of the file that the user can upload to the server 
        if self.avatar and self.avatar.size > MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"Avatar cannot exceed {MAX_SIZE_MB} MB")

        if self.avatar:
            with Image.open(self.avatar) as img:
                max_width = 800
                max_height = 800

                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.ANTIALIAS)
                    
                    buffer = BytesIO()
                    img.save(buffer, format=img.format)
                    self.avatar.save(self.avatar.name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)


    def __str__(self):
        try:
            name = self.name or "Null"
        except Exception:
            name = "Null"
        company = "Company" if self.this_customer_is_a_company else "Null"
        return f"{name} ({company})"
