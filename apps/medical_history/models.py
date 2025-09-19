from django.db import models
from django.conf import settings
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from django.utils import timezone
from ..customers.models import Customer
from ..services.models import Consultation, ProfessionalData, Specialty

#-----------------------------------------------------------------APP DOCTOR--------------------------------------------------
#this table is for the information medical of the patient
class MedicalInformation(models.Model):
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="medical_informations", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="medical_informations", null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="medical_information")
    skull = models.CharField(max_length=100, blank=False, null=False) #this is a Identifier

    #Detailed medical information
    BLOOD_TYPE_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]
    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_TYPE_CHOICES,
        blank=True,
        null=True
    )

    height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # It can be calculated

    chronic_conditions = EncryptedTextField(blank=True, null=True)
    allergies = EncryptedTextField(blank=True, null=True)
    medications = EncryptedTextField(blank=True, null=True)  # Current medications
    surgeries = EncryptedTextField(blank=True, null=True)
    immunizations = EncryptedTextField(blank=True, null=True)  # vaccines
    family_history = EncryptedTextField(blank=True, null=True)  # hereditary diseases

    lifestyle = EncryptedTextField(blank=True, null=True)  # Ej: Smoker, alcohol, exercise, diet

    emergency_contact_name = EncryptedCharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = EncryptedCharField(max_length=20, blank=True, null=True)
    emergency_contact_relation = EncryptedCharField(max_length=50, blank=True, null=True)

    last_visit = models.DateField(blank=True, null=True)
    notes = EncryptedTextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    info_other_doctor = EncryptedTextField(blank=True, null=True) #this is the information of other doctors that the patient can need

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'skull'], name='unique_skull_per_company')
        ]

    def __str__(self):
        return f"History of {self.customer}"
    
class Prescription(models.Model):
    #data of the compnay and branch
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="prescriptions", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="prescriptions", null=True, blank=True)
    doctor = models.ForeignKey(
        ProfessionalData,
        on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )


    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("finalized", "Finalizada"),
        ("canceled", "Cancelada"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )


    date_prescribed = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)


    updated_at = models.DateTimeField(auto_now=True)

    #this is for save the change of the Prescription 
    history = models.JSONField(blank=True, null=True)   #[{"timestamp":..., "notes":..., "items":[...]}]


    def save(self, *args, **kwargs):
        # Guardar snapshot si ya existe la receta y cambió
        if self.pk:
            old = Prescription.objects.filter(pk=self.pk).first()
            if old:
                snapshot = {
                    "timestamp": timezone.now().isoformat(),
                    "notes": old.notes,
                    "status": old.status,
                    "items": [
                        {
                            "medicine_name": item.medicine_name,
                            "dosage": item.dosage,
                            "frequency": item.frequency,
                            "duration": item.duration,
                            "instructions": item.instructions,
                        }
                        for item in old.items.all()
                    ]
                }
                if not self.history:
                    self.history = []
                self.history.append(snapshot)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} - {self.date_prescribed.date()} ({self.status})"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="prescriptions_item"
    )
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)  # example. 500mg
    frequency = models.CharField(max_length=100)  # example. for 8 hours
    duration = models.CharField(max_length=100)  # example. 7 days
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.dosage})"
    
class LabResult(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="lab_results")
    professional = models.ForeignKey(ProfessionalData, on_delete=models.SET_NULL, null=True, blank=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True)
    test_name = models.CharField(max_length=200)
    result = models.TextField()
    unit = models.CharField(max_length=50, blank=True, null=True)
    normal_range = models.CharField(max_length=100, blank=True, null=True)
    date_performed = models.DateField()
    notes = models.TextField(blank=True, null=True)
    file_url = models.FileField(upload_to="lab_results/", blank=True, null=True)

    def __str__(self):
        return f"{self.test_name} - {self.customer}"
