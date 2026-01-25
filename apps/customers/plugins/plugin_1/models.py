from django.db import models
from apps.customers.models import Customers

class Customer_address(models.Model):
    customers = models.OneToOneField(
        Customers, on_delete=models.CASCADE, related_name="address_extension"
    )

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)