from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import uuid

#here load the key of encrypt for encrypt the information of the customer
from cryptography.fernet import Fernet
import os

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
        db_table = "customer.customer_source"
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
        db_table = "customer.customer_type"
        verbose_name = "Customer Type"
        verbose_name_plural = "Customer Types"
        unique_together = ("company", "name") #this is for that not exist type repeat in the company 

    def __str__(self):
        return self.name
    

# upload_to dinamic
def customer_avatar_path(instance, filename):
    # instance.company.id, instance.branch.id
    ext = filename.split('.')[-1]
    return f"customers/company_{instance.company.id}/branch_{instance.branch.id}/{uuid.uuid4().hex}_avatar.{ext}"


class Customer(models.Model):
    #------personal information------
    id = models.BigAutoField(primary_key=True)  
    avatar = models.ImageField(upload_to=customer_avatar_path, blank=True, null=True)
    _name = models.BinaryField(db_column="name", blank=True, null=True)
    _email = models.BinaryField(db_column="email", blank=True, null=True)
    _phone = models.BinaryField(db_column="phone", blank=True, null=True)
    _cellphone = models.BinaryField(db_column="cellphone", blank=True, null=True)
    
    #------information of address------
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO code (ej: MX, US)
    _address = models.BinaryField(db_column="address", blank=True, null=True)
    _city = models.BinaryField(db_column="city", blank=True, null=True)
    _state = models.BinaryField(db_column="state", blank=True, null=True)
    _postal_code = models.BinaryField(db_column="postal_code", blank=True, null=True)
    _num_ext = models.BinaryField(db_column="num_ext", blank=True, null=True)
    _num_int = models.BinaryField(db_column="num_int", blank=True, null=True)
    _reference = models.BinaryField(db_column="reference", blank=True, null=True)

    #--information of the company------
    this_customer_is_a_company = models.BooleanField(default=False)
    _company_name = models.BinaryField(db_column="company_name", blank=True, null=True)
    _contact_name = models.BinaryField(db_column="contact_name", blank=True, null=True)
    _contact_email = models.BinaryField(db_column="contact_email", blank=True, null=True)
    _contact_cellphone = models.BinaryField(db_column="contact_cellphone", blank=True, null=True)
    _contact_phone = models.BinaryField(db_column="contact_phone", blank=True, null=True)
    _website = models.BinaryField(db_column="website", blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    #--information of the customer in the company------
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="customer_customer", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="customer_customer", null=True, blank=True)
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


    #------------Getters and setters para cifrar/desifrar campos sensibles------------
    def _get_field(self, field):
        val = getattr(self, f"_{field}")

        if val:
            return cipher.decrypt(val).decode()
        return None

    def _set_field(self, field, value):
        if value:
            setattr(self, f"_{field}", cipher.encrypt(value.encode()))
        else:
            setattr(self, f"_{field}", None)

    @property
    def name(self): return self._get_field("name")
    @name.setter
    def name(self, value): self._set_field("name", value)

    @property
    def email(self): return self._get_field("email")
    @email.setter
    def email(self, value): self._set_field("email", value)

    @property
    def phone(self): return self._get_field("phone")
    @phone.setter
    def phone(self, value): self._set_field("phone", value)

    @property
    def cellphone(self): return self._get_field("cellphone")
    @cellphone.setter
    def cellphone(self, value): self._set_field("cellphone", value)

    @property
    def address(self): return self._get_field("address")
    @address.setter
    def address(self, value): self._set_field("address", value)

    @property
    def city(self): return self._get_field("city")
    @city.setter
    def city(self, value): self._set_field("city", value)

    @property
    def state(self): return self._get_field("state")
    @state.setter
    def state(self, value): self._set_field("state", value)

    @property
    def postal_code(self): return self._get_field("postal_code")
    @postal_code.setter
    def postal_code(self, value): self._set_field("postal_code", value)

    @property
    def num_ext(self): return self._get_field("num_ext")
    @num_ext.setter
    def num_ext(self, value): self._set_field("num_ext", value)

    @property
    def num_int(self): return self._get_field("num_int")
    @num_int.setter
    def num_int(self, value): self._set_field("num_int", value)

    @property
    def reference(self): return self._get_field("reference")
    @reference.setter
    def reference(self, value): self._set_field("reference", value)

    @property
    def company_name(self): return self._get_field("company_name")
    @company_name.setter
    def company_name(self, value): self._set_field("company_name", value)

    @property
    def contact_name(self): return self._get_field("contact_name")
    @contact_name.setter
    def contact_name(self, value): self._set_field("contact_name", value)

    @property
    def contact_email(self): return self._get_field("contact_email")
    @contact_email.setter
    def contact_email(self, value): self._set_field("contact_email", value)

    @property
    def contact_cellphone(self): return self._get_field("contact_cellphone")
    @contact_cellphone.setter
    def contact_cellphone(self, value): self._set_field("contact_cellphone", value)

    @property
    def contact_phone(self): return self._get_field("contact_phone")
    @contact_phone.setter
    def contact_phone(self, value): self._set_field("contact_phone", value)

    @property
    def website(self): return self._get_field("website")
    @website.setter
    def website(self, value): self._set_field("website", value)


    class Meta:
        db_table = "customer.customer"
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
            #open the image use Pillow
            img = Image.open(self.avatar)
            
            #change the resolution max
            max_width = 800
            max_height = 800

            #Resize if it is too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.ANTIALIAS)
                
                # save the new image in the memory
                buffer = BytesIO()
                img.save(buffer, format=img.format)
                self.avatar.save(self.avatar.name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.name} ({'Company' if self.this_customer_is_a_company else 'Null'})"
