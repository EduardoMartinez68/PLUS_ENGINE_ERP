from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from core.models import CustomUser
from apps.sales.models import Sale
class Contract(models.Model):
    #---------------this is for sign the treatment---------------
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE) #save the relation with the sale
    contract_text = EncryptedTextField() #the contract is encrypted for privacity

    #----------------------information of the customer-------------------------
    patiente_signature_json = models.JSONField() #this is for save the signature of the customer
    patiente_signature_image = models.ImageField(upload_to="signatures/", null=True, blank=True) #optional 

    patient_name = EncryptedCharField(max_length=255) #the name of who signed
    patient_signed_at = models.DateTimeField(auto_now_add=True)
    patient_ip  = models.GenericIPAddressField(null=True, blank=True) #ip of the signature

    #----------------------information of the employee of the company-------------------------
    company_signature_json = models.JSONField() #this is for save the signature of the customer
    company_signature_image = models.ImageField(upload_to="signatures/", null=True, blank=True) #optional 

    company_name = EncryptedCharField(max_length=255) #the name of the employee that figned
    company_signed_at = models.DateTimeField(auto_now_add=True)
    company_ip  = models.GenericIPAddressField(null=True, blank=True) #ip of the signature


    #this is for know if the signed is activate
    is_signed = models.BooleanField(default=False) #status of the signed 


    #this is for know that user do this Contract 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True, blank=True)#here you can create the body of the database 


    class Meta:
        constraints = [
            #this is for that only exist a Contract for sale
            models.UniqueConstraint(fields=['sale'], name='unique_contract_per_sale')
        ]