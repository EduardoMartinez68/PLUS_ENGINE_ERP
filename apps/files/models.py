#here you can create the body of the database 
from django.db import models
from django.utils import timezone
from core.models import CustomUser, Company, Branch
from django.core.validators import FileExtensionValidator





class Folder(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, db_column='company')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, db_column='branch')
    
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subfolders'
    )
    color = models.CharField(
        max_length=7,  # example: "#3A7BD5"
        default="#3A7BD5",
        help_text="Color hexadecimal for the folder"
    )

    #information basic of creation
    created_at = models.DateTimeField(default=timezone.now)
    creator_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, db_column='employee')

    class Meta:
        verbose_name = 'folder'
        verbose_name_plural = 'folders'

        # 🔒 Avoid folders with the same name within the same branch and same parent
        unique_together = ('branch', 'parent', 'name')

    def __str__(self):
        return self.name

class FolderPermission(models.Model):
    #this is for that only the user that be save here can watch the information of the folders
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    #character of the folder
    can_read = models.BooleanField(default=True)
    can_copy = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    can_upload_file = models.BooleanField(default=False)
    can_move_file = models.BooleanField(default=False)
    can_update_file = models.BooleanField(default=False)
    can_copy_file = models.BooleanField(default=False)
    can_delete_file = models.BooleanField(default=False)

    can_change_the_permission = models.BooleanField(default=False)
    can_add_members = models.BooleanField(default=False)
    can_delete_members = models.BooleanField(default=False)

    class Meta:
        unique_together = ('folder', 'user')

class File(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, db_column='company')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, db_column='branch')
    folder = models.ForeignKey(
        Folder, 
        on_delete=models.CASCADE, 
        related_name='files'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    #character of the files
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'png', 'jpeg', 'doc', 'docx', 'xls', 'xlsx']
            )
        ]
    )
    
    url = models.URLField(max_length=500, blank=True, null=True)
    anchored = models.BooleanField(default=False)
    size = models.PositiveIntegerField(default=0)  # En bytes
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', null=True, blank=True) #this is for show the miniature

    uploaded_at = models.DateTimeField(default=timezone.now)
    upload_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, db_column='employee')

    class Meta:
        verbose_name = 'file'
        verbose_name_plural = 'files'
        constraints = [
            models.UniqueConstraint(
                fields=['folder', 'key'],
                name='unique_key_per_folder'
            )
        ]
        ordering = ['-uploaded_at']  # Newest first

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Calculate file size automatically
        if self.file and hasattr(self.file, 'size'):
            self.size = self.file.size
        super().save(*args, **kwargs)