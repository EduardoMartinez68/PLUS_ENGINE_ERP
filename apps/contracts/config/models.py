# Model definitions go here
from django.db import models

class Contracts(models.Model):
    user_id = models.BigIntegerField(null=True, blank=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    content_html = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"contracts"."contract"'  # schema.tabla
        verbose_name = 'Contracts'
        verbose_name_plural = 'Contracts'

    def __str__(self):
        return self.name
