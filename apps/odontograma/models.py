#here you can create the body of the database 
from django.db import models
from encrypted_model_fields.fields import EncryptedTextField, EncryptedCharField
from apps.customers.models import Customer
from django.utils import timezone
from core.models import CustomUser, Branch, Company

def create_odontogram_for_patient(medical_info, include_deciduous=False):
    #this function is for create all the tooth of the mouth when the odontograma be create
    odontogram = Odontogram.objects.create(medical_information=medical_info)
    teeth_list = FDI_TEETH + (FDI_TEETH_DECIDUOUS if include_deciduous else [])
    for number, key in teeth_list:
        Tooth.objects.create(odontogram=odontogram, FDI_number=number, name_key=key)
    return odontogram

class Odontogram(models.Model):
    """
    Represents a complete dental chart associated with a client.
    A patient can have only one odontogram per company, but the odontogram
    can have multiple historical versions (HistoryOdontogram).
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="odontograms"
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="odontograms"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="odontogram"
    )
    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="odontograms"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "customer"],
                name="unique_odontogram_per_customer_per_company"
            )
        ]

    def __str__(self):
        return f"Odontogram of {self.customer} ({self.company.name})"
    
class HistoryOdontogram(models.Model):
    """
    It represents the history of odotongrama of the patientes and know which the update
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="odontograms"
    )

    key = models.CharField(max_length=150, null=False)
    notes = EncryptedTextField(blank=True, null=True)


    #this is for know when was create or when was last update
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blocked = models.BooleanField(default=False, help_text="Indicates if the odontogram is locked and cannot be modified.")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Odontogram of {self.customer}"

class Tooth(models.Model):
    """
    This is the model of a teeth in the odontograma.
    """
    historyodontogram = models.ForeignKey(
        HistoryOdontogram,
        on_delete=models.CASCADE,
        related_name="teeth"
    )


    
    FDI_TEETH = [
        #-----------------------------------------theet adult---------------------------------------------
        # Quadrant 1 (Upper Right)
        (11, "odontogram.tooth.upper_right.central_incisor"),
        (12, "odontogram.tooth.upper_right.lateral_incisor"),
        (13, "odontogram.tooth.upper_right.canine"),
        (14, "odontogram.tooth.upper_right.first_premolar"),
        (15, "odontogram.tooth.upper_right.second_premolar"),
        (16, "odontogram.tooth.upper_right.first_molar"),
        (17, "odontogram.tooth.upper_right.second_molar"),
        (18, "odontogram.tooth.upper_right.third_molar"),

        # Quadrant 2 (Upper Left)
        (21, "odontogram.tooth.upper_left.central_incisor"),
        (22, "odontogram.tooth.upper_left.lateral_incisor"),
        (23, "odontogram.tooth.upper_left.canine"),
        (24, "odontogram.tooth.upper_left.first_premolar"),
        (25, "odontogram.tooth.upper_left.second_premolar"),
        (26, "odontogram.tooth.upper_left.first_molar"),
        (27, "odontogram.tooth.upper_left.second_molar"),
        (28, "odontogram.tooth.upper_left.third_molar"),

        # Quadrant 3 (Lower Left)
        (31, "odontogram.tooth.lower_left.central_incisor"),
        (32, "odontogram.tooth.lower_left.lateral_incisor"),
        (33, "odontogram.tooth.lower_left.canine"),
        (34, "odontogram.tooth.lower_left.first_premolar"),
        (35, "odontogram.tooth.lower_left.second_premolar"),
        (36, "odontogram.tooth.lower_left.first_molar"),
        (37, "odontogram.tooth.lower_left.second_molar"),
        (38, "odontogram.tooth.lower_left.third_molar"),

        # Quadrant 4 (Lower Right)
        (41, "odontogram.tooth.lower_right.central_incisor"),
        (42, "odontogram.tooth.lower_right.lateral_incisor"),
        (43, "odontogram.tooth.lower_right.canine"),
        (44, "odontogram.tooth.lower_right.first_premolar"),
        (45, "odontogram.tooth.lower_right.second_premolar"),
        (46, "odontogram.tooth.lower_right.first_molar"),
        (47, "odontogram.tooth.lower_right.second_molar"),
        (48, "odontogram.tooth.lower_right.third_molar"),

        #-----------------------------------------theet kid---------------------------------------------
        # Top right
        (51, "odontogram.tooth.upper_right.primary_central_incisor"),
        (52, "odontogram.tooth.upper_right.primary_lateral_incisor"),
        (53, "odontogram.tooth.upper_right.primary_canine"),
        (54, "odontogram.tooth.upper_right.primary_first_molar"),
        (55, "odontogram.tooth.upper_right.primary_second_molar"),

        # Top left
        (61, "odontogram.tooth.upper_left.primary_central_incisor"),
        (62, "odontogram.tooth.upper_left.primary_lateral_incisor"),
        (63, "odontogram.tooth.upper_left.primary_canine"),
        (64, "odontogram.tooth.upper_left.primary_first_molar"),
        (65, "odontogram.tooth.upper_left.primary_second_molar"),

        # Lower left
        (71, "odontogram.tooth.lower_left.primary_central_incisor"),
        (72, "odontogram.tooth.lower_left.primary_lateral_incisor"),
        (73, "odontogram.tooth.lower_left.primary_canine"),
        (74, "odontogram.tooth.lower_left.primary_first_molar"),
        (75, "odontogram.tooth.lower_left.primary_second_molar"),

        # Lower right
        (81, "odontogram.tooth.lower_right.primary_central_incisor"),
        (82, "odontogram.tooth.lower_right.primary_lateral_incisor"),
        (83, "odontogram.tooth.lower_right.primary_canine"),
        (84, "odontogram.tooth.lower_right.primary_first_molar"),
        (85, "odontogram.tooth.lower_right.primary_second_molar"),
    ]

    # number global of the tooth (FDI)
    FDI_number = models.PositiveSmallIntegerField(unique=True) #this is unique because not exist more tooth in the mouth
    name_key = models.CharField(max_length=200, blank=True, null=False , choices=FDI_TEETH)  # example: “Incisivo central superior derecho”



    #status of the tooth
    STATUS_CHOICES = [
        ("healthy", "Sano"),
        ("caries", "Caries"),
        ("missing", "Ausente"),
        ("filled", "Empaste"),
        ("extracted", "Extraído"),
        ("implanted", "Implante"),
        ("crown", "Corona"),
        ("fractured", "Fracturado"),
        ("endodontic", "Endodoncia"),
        ("other", "Otro"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="healthy")






    # Diagnostic and observation fields
    diagnosis = EncryptedTextField(blank=True, null=True)
    notes = EncryptedTextField(blank=True, null=True)

    # Detailed condition by surface
    surface_occlusal = models.CharField(max_length=50, blank=True, null=True)
    surface_mesial = models.CharField(max_length=50, blank=True, null=True)
    surface_distal = models.CharField(max_length=50, blank=True, null=True)
    surface_lingual = models.CharField(max_length=50, blank=True, null=True)
    surface_buccal = models.CharField(max_length=50, blank=True, null=True)

    # Information on treatments applied
    treatments = EncryptedTextField(blank=True, null=True)




    #information of creation and of update
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_teeth"
    )

    class Meta:
        unique_together = ("odontogram", "FDI_number")
        ordering = ["FDI_number"]

    def __str__(self):
        return f"Diente {self.FDI_number} - {self.get_status_display()}"



class OdontogramFile(models.Model):
    """
    Relationship between an odontogram and one or more files (x-rays, photos, documents, etc.).
    """
    odontogram = models.ForeignKey(
        "Odontogram",
        on_delete=models.CASCADE,
        related_name="odontogram_files"
    )
    file = models.ForeignKey(
        "File",
        on_delete=models.CASCADE,
        related_name="odontogram_links"
    )


    #this be the type of files that the doctor can upload 
    FILE_TYPE_CHOICES = [
        ("xray", "Radiografía"),
        ("photo", "Fotografía"),
        ("document", "Documento"),
        ("payment", "Historial de pago"),
        ("lab_report", "Informe de laboratorio"),
        ("other", "Otro"),
    ]
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default="other"
    )


    visible_to_patient = models.BooleanField(default=False)  #this is for that the customer can see the file and note of the doctor
    description_fot_the_patient = models.TextField(blank=True, null=True) #this a description extra for the patient
    
    #information of update
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="odontogram_uploaded_files"
    )

    class Meta:
        verbose_name = "Odontogram File"
        verbose_name_plural = "Odontogram Files"
        constraints = [
            models.UniqueConstraint(
                fields=["odontogram", "file"],
                name="unique_file_per_odontogram"
            )
        ]
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"File {self.file.name} for Odontogram {self.odontogram.id}"