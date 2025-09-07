from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

class CustomerSource(models.Model):
    """
    Customer source (how they contacted us or who referred them).
    Example: Website, referral, Facebook ad, trade show, e-commerce platform.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "customer.customer_source"
        verbose_name = "Customer Source"
        verbose_name_plural = "Customer Sources"

    def __str__(self):
        return self.name
    

class CustomerType(models.Model):
    """
    Type or category of customer. 
    Example: Customer, Supplier, Distributor, Patient, Student.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "customer.customer_type"
        verbose_name = "Customer Type"
        verbose_name_plural = "Customer Types"

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    #--personal information
    id = models.BigAutoField(primary_key=True)  
    avatar = models.ImageField(upload_to="customers/", blank=True, null=True)
    name = models.CharField(max_length=300)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    cellphone = models.CharField(max_length=50, blank=True, null=True)

    country = models.CharField(max_length=2, blank=True, null=True)  # ISO code (ej: MX, US)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    #--information of the company 
    this_customer_is_a_company = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=150, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_cellphone = models.CharField(max_length=20, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    #--information of the customer in the company
    id_company = models.BigIntegerField(blank=True, null=True)
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


    creation_date = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = "customer.customer"
        indexes = [
            models.Index(fields=["name"], name="idx_customer_name"),
            models.Index(fields=["email"], name="idx_customer_email"),
            models.Index(fields=["cellphone"], name="idx_customer_cellphone"),
            models.Index(fields=["id_company"], name="idx_customer_id_company"),
            models.Index(fields=["activated"], name="idx_customer_activated"),
            models.Index(fields=["company_name"], name="idx_customer_company_name"),
            models.Index(fields=["email", "id_company"], name="idx_customer_email_branch"),
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
