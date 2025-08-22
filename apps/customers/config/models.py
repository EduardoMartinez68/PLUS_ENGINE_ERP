# Model definitions go here
from django.db import models

class Customer(models.Model):
    id_branch = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=300)
    email = models.EmailField(blank=True, null=True)
    this_customer_is_a_company = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    rfc = models.CharField(max_length=50, blank=True, null=True)
    curp = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    cellphone = models.CharField(max_length=50, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=False)
    country = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = '"company"."customer"'  # schema.tabla
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name