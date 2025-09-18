from django.db import models
from django.conf import settings
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField, EncryptedJSONField
from django.utils import timezone
#-----------------------------------------------SERVICES------------------------------------------------------------------
class Specialty(models.Model):
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)

    name = models.CharField(max_length=100, unique=True)  # E.g. Pediatrics, Cardiology, divorce lawyer
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class ProfessionalData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_profile"
    )

    #information of the professional
    specialties = models.ManyToManyField("Specialty", related_name="professionals")
    license_number = models.CharField(max_length=50, unique=True)

    #information of contact of job
    phone = EncryptedCharField(db_column="phone", blank=True, null=True, max_length=20)
    email = EncryptedCharField(db_column="email", blank=True, null=True, max_length=100)
    office_address  = EncryptedCharField(db_column="office_address", blank=True, null=True, max_length=100) 

    #information of study 
    license_country = models.CharField(max_length=2, blank=True, null=True)
    university = EncryptedCharField(db_column="university", blank=True, null=True, max_length=100)
    degree_title = models.CharField(max_length=150, blank=True, null=True)  #example Surgeon, Lawyer, Civil Engineer
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    license_expiration_date = models.DateField(blank=True, null=True)
    
    #portfolio professional
    website = models.URLField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)

    #information of the system
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.license_number} - {self.specialty}"

class Consultation(models.Model):
    #information of the consultation 
    skull = models.CharField(max_length=100, blank=False, null=False) #this is a Identifier
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #the user that do this consultation 
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.SET_NULL,  # If the client is deleted, the consultation remains null
        null=True, #the patient can be null if the doctor do consultation to the public
        blank=True,
        related_name="consultations"
    )
    professional  = models.ForeignKey(
        "ProfessionalData",
        on_delete=models.SET_NULL,  #If the doctor is deleted, the consultation remains null
        null=True,
        blank=True,
        related_name="consultations"
    )
    appoint = models.ForeignKey(
        "Appointment",
        on_delete=models.SET_NULL,  # If the client is deleted, the consultation remains null
        null=True, #the patient can be null if the doctor do consultation to the public
        blank=True,
        related_name="consultations"
    )

    #information basic of the consultation 
    priority = models.SmallIntegerField(default=0)
    topic = EncryptedTextField(blank=True, null=True)  # Tema de la reunión o consulta
    discussion_points = EncryptedJSONField(blank=True, null=True)  # Puntos tratados
    conclusions = EncryptedTextField(blank=True, null=True)  # Conclusiones o decisiones
    action_items = EncryptedJSONField(blank=True, null=True)  # Acciones a seguir
    notes = EncryptedTextField(blank=True, null=True)  # Notas generales
    attachments = EncryptedJSONField(blank=True, null=True)  # Archivos relacionados son solo links




    #information of the character of the consultation
    STATUS_CHOICES = [
        ("scheduled"),
        ("completed"),
        ("canceled"),
    ]
    status = models.CharField( #here is for save the status of the consultation 
        max_length=10,
        choices=STATUS_CHOICES,
        default="scheduled"
    )
    consultation_type = models.CharField(
        max_length=20,
        choices=[("in_person"), ("online"), ("home"), ("remote")],
        default="in_person"
    )

    #price of the consultation 
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio de la consulta"
    )
    currency = models.CharField(
        max_length=10, 
        default="MXN", 
        help_text="Query currency (example. MXN, USD, EUR)"
    )


    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now) #when be do this consultation 

    #if the consultation was update , save this information 
    updated_at = models.DateTimeField(auto_now=True) 
    updated_by = models.ForeignKey(
        "CustomUser", on_delete=models.SET_NULL, null=True, blank=True
    )
    history_information = EncryptedJSONField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'skull'], name='unique_skull_per_company_consultation')
        ]

    def __str__(self):
        return f"{self.professional} the {self.date.strftime('%Y-%m-%d %H:%M')}"
    




#------------------------------------------------FILES-----------------------------------------------------------------------
class Document(models.Model):
    """
    Modelo para representar documentos subidos al sistema.
    Se puede usar para PDFs, Excel, imágenes, etc.
    """
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que subió el documento")
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)

    title = EncryptedCharField(max_length=200, blank=False, null=False, help_text="Nombre o título del documento")
    description = EncryptedTextField(blank=True, null=True, help_text="Descripción del documento")
    file_type = models.CharField(max_length=50, blank=True, null=True, help_text="Tipo de archivo: pdf, excel, image, etc.")
    file_url = EncryptedCharField(max_length=500, blank=True, null=True, help_text="URL o ruta del archivo")
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

#------------------------------------------------TASK-----------------------------------------------------------------------
class Task(models.Model):
    """
    Modelo para representar tareas que pueden estar asociadas a expedientes.
    """
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="specialty", null=True, blank=True)

    title = EncryptedCharField(max_length=200, blank=False, null=False, help_text="Título de la tarea")
    description = EncryptedTextField(blank=True, null=True, help_text="Descripción detallada de la tarea")
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", help_text="Estado de la tarea")
    priority = models.SmallIntegerField(default=0, help_text="Prioridad de la tarea")
    
    due_date = models.DateTimeField(blank=True, null=True, help_text="Fecha límite para completar la tarea")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario asignado a la tarea")

    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

#-------------------------------------------------------------------------------projects------------------------------------------------------------
#esta app servira para los abogados, doctores, dentistas, etc y sera para que ellos tengan sus proyectos y casos organizados, todo en un simple proceso. 
# Se tratara de guardar la informacion mas importante y todos los archivos o juntas relacionadas. Esto podria servir tambien para la reuniones en juntas o proyectos de empresa
#esta app se agregara en PLUS 2.0 junto a la app de areas obvriamente.
class Record(models.Model):
    """
    Modelo genérico para gestionar expedientes de clientes/proyectos/casos
    aplicable a doctores, abogados, contadores, consultores, etc.
    """
    # Información general
    skull = models.CharField(max_length=100, blank=False, null=False, help_text="Identificador único por empresa")
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="records", null=True, blank=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="records", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #the user that be do this record
    customer = models.ForeignKey("core.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="records")
    

    # Información principal del expediente
    title = EncryptedCharField(max_length=200, blank=True, null=True, help_text="Título del expediente o caso")
    description = EncryptedTextField(blank=True, null=True, help_text="Descripción general del expediente")
    status = models.CharField(
        max_length=20,
        choices=[
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("archived", "Archived"),
        ],
        default="open",
        help_text="Estado general del expediente"
    )
    priority = models.SmallIntegerField(default=0, help_text="Prioridad del expediente")

    # Información detallada y flexible
    invoices = EncryptedJSONField(blank=True, null=True, help_text="Facturas o cobros asociados al expediente")
    notes = EncryptedTextField(blank=True, null=True, help_text="Notas generales")
    
    # Historial de cambios del expediente
    history = EncryptedJSONField(blank=True, null=True, help_text="Registro de cambios y versiones del expediente")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Último usuario que actualizó el expediente")

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'skull'], name='unique_skull_per_company_record')
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title or self.skull} ({self.customer})"
    



#this is for save all the consultation that be in the record for example in a case for a lawyer or a consultation for a doctor
class HistoryConsultation(models.Model):
    record = models.ForeignKey(
        "Record", 
        on_delete=models.CASCADE, 
        related_name="history_consultations",
        help_text="Expediente o caso al que pertenece esta consulta"
    )
    professional = models.ForeignKey(
        "ProfessionalData", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="history_consultations",
        help_text="Profesional que realizó la consulta o reunión"
    )
    customers = models.ForeignKey(
        "core.Customer", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="history_consultations",
        help_text="Cliente involucrado en la consulta"
    )


    class Meta:
        ordering = ["-consultation_date"]
        verbose_name = "History Consultation"
        verbose_name_plural = "History Consultations"

#this is for save all the document that the user need
class RecordDocument(models.Model):
    """
    Tabla intermedia para relacionar documentos con expedientes (Records)
    """
    record = models.ForeignKey("Record", on_delete=models.CASCADE, related_name="record_documents")
    document = models.ForeignKey("Document", on_delete=models.CASCADE, related_name="document_records")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que asoció el documento al expediente")
    notes = EncryptedTextField(blank=True, null=True, help_text="Notas sobre la relación expediente-documento")
    added_at = models.DateTimeField(auto_now_add=True, default=timezone.now)

    class Meta:
        unique_together = ('record', 'document')
        ordering = ['-added_at']

    def __str__(self):
        return f"Documento '{self.document}' en expediente '{self.record}'"
    
class RecordTask(models.Model):
    """
    Tabla intermedia para relacionar Records con Tasks
    """
    record = models.ForeignKey("Record", on_delete=models.CASCADE, related_name="record_tasks")
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="task_records")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que agregó la tarea al expediente")
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata adicional opcional
    notes = EncryptedTextField(blank=True, null=True, help_text="Notas sobre la relación entre expediente y tarea")

    class Meta:
        unique_together = ('record', 'task')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"Tarea '{self.task}' en expediente '{self.record}'"
    