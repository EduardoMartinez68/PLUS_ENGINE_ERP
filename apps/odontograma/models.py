#here you can create the body of the database 
from django.db import models
from encrypted_model_fields.fields import EncryptedTextField, EncryptedCharField
from apps.customers.models import Customer
from apps.files.models import File
from django.utils import timezone
from core.models import CustomUser, Branch, Company
from django.core.validators import MinValueValidator, MaxValueValidator

def create_odontogram_for_patient(medical_info, include_deciduous=False):
    #this function is for create all the tooth of the mouth when the odontograma be create
    odontogram = Odontogram.objects.create(medical_information=medical_info)
    teeth_list = FDI_TEETH + (FDI_TEETH_DECIDUOUS if include_deciduous else [])
    for number, key in teeth_list:
        Tooth.objects.create(odontogram=odontogram, FDI_number=number, name_key=key)
    return odontogram

class OdontogramSetting(models.Model):
    """
    Here we will to save the setting of the odontogram that the user use in his job
    example the system of the odontograms or his emails and chraracteres
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="odontogram_settings"
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="odontogram_settings"
    )
    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="odontogram_settings"
    )

    typeSystem=models.PositiveSmallIntegerField(
        default=1,
        choices=[
            (1, "FDI"),
            (2, "Universal")
        ],
        null=False
    )

    #colors of the options
    color_caries = models.CharField(max_length=7, default="#FF0000") 

    #here we will to save the options that the dentist can do in his office 
    default_treatments = models.JSONField(default=dict)
    # example: {"caries": "Relleno composite", "extracción": "Extracción simple"}

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "doctor"],
                name="unique_odontogram_per_doctor_per_company"
            )
        ]

    def __str__(self):
        return f"Odontogram of {self.doctor} ({self.company.name})"
    

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
    svg = EncryptedTextField(null=True)

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


    #this variable save all the translate of the tooth that we going to use in the frontend for translate the tooth
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
    name_key = models.CharField(max_length=200, blank=True, null=False , choices=FDI_TEETH)  # example: “odontogram.tooth.upper_right.central_incisor (Incisivo central superior derecho)”


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

    # Detailed condition by surface
    # Superficies del diente (útil para odontogramas visuales)
    surfaces = models.JSONField(default=dict, blank=True)
    # example:
    # {
    #   "mesial": {"caries": True, "restauracion": False, "Notes": ""},
    #   "distal": {"caries": False, "restauracion": True},
    #   "oclusal": {"fisura": True},
    #   "lingual": {},
    #   "vestibular": {}
    # }

    caries_depth = models.PositiveSmallIntegerField(
        default=0,
        choices=[
            (0, "No cavities"),
            (1, "Affected enamel"),
            (2, "affected dentin"),
            (3, "Close to the pulp"),
            (4, "It compromises the pulp")
        ],
        help_text="Indicates the level of depth of the caries on a scale of 0 to 4."
    )
    has_tartar=models.BooleanField(default=False)

    '''
    0--normal
    1--inflamed
    2--bleeding
    '''
    status_gum=models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        default=0
    )

    '''
    0--WITHOUT MOBILITY
    1--leve 
    2--moderate
    3--severe
    '''
    mobility=models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        default=0
    )

    # Diagnostic and observation fields
    diagnosis = EncryptedTextField(blank=True, null=True)
    notes = EncryptedTextField(blank=True, null=True)
    
    # Information on treatments applied
    treatments = EncryptedTextField(blank=True, null=True)

    # Visual state of the tooth in SVG format
    #this variable be use for save the draw of the status of the tooth in format svg
    svg_state = models.JSONField(default=dict, blank=True, help_text="SVG code that represents the current visual state of the tooth.")
    # example:
    # {
    #   {"caries", "corona", ...}
    # }





    #information of creation and of update
    last_checkup = models.DateField(null=True, blank=True)
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
        unique_together = ("historyodontogram", "FDI_number")
        ordering = ["FDI_number"]

    def __str__(self):
        return f"Diente {self.FDI_number} - {self.get_status_display()}"

class OdontogramFile(models.Model):
    """
    Relationship between an odontogram and one or more files (x-rays, photos, documents, etc.).
    """
    odontogram = models.ForeignKey(
        Odontogram,
        on_delete=models.CASCADE,
        related_name="odontogram_files"
    )
    file = models.ForeignKey(
        File,
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