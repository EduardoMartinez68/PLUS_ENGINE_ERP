'''
this both functions are for calculate the space that the user have in the server and if can upload more 
files to his count. If the user is use the software in desktop, the can upload all the files that need unlimited.
'''
from django.db.models import Sum
from ..models import Folder, FolderPermission, File
from cryptography.fernet import Fernet #this is for encrypt the file
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
import os
from dotenv import load_dotenv
load_dotenv()

#get the type of software 
TYPE_VERSION = os.environ.get('TYPE_VERSION')

#get the key of encrypt that is in our file .env
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY').encode()
f = Fernet(FIELD_ENCRYPTION_KEY)


def user_storage_used(user):
    return File.objects.filter(upload_user=user).aggregate(total=Sum('size'))['total'] or 0

def can_upload(user, filesize):
    limit = get_limit_of_the_user() * 1024 * 1024 * 1024  # 1 GiB
    return user_storage_used(user) + filesize <= limit

def get_limit_of_the_user():
    if TYPE_VERSION=='DESKTOP':
        return True
    

    #here we will see the pack that have the user in the subscription and return the size of his space
    #pack 1==1 GiB
    #pack 2==5 GiB
    return 1

def upload_file(user, dataFile):
    #get the basic information of the file 
    file=dataFile.get("file")
    name=dataFile.get("name")

    #now we will to eval if can save this file because the file have all the information that we need
    if not file:
        return {"success": False, "message": "files.message.not-exist-file", "error": "You need upload a file"}
    
    if not name or not name.strip():
        if file: #now we will see if exist the file
            name = file.name #if not have name of file we will to save with the name of the file that the user upload
        else:
            # when there is no name or file 
            return {"success": False, "message": "files.message.not-exist-file", "error":"You need upload a file"}

    #we will see if the file not be very big for the memory of the user
    if not can_upload(user, file.size):
        return {"success": False, "message": "file.message.not-can-upload-the-file-because-not-have-memory", "error":"insufficient memory"}
    

    #here we will to read the file and the encrypt
    container = file.read() 
    container_encrypt = f.encrypt(container)

    #when all the information is success and already encrypt the file, now we will to save 
    key = get_random_string(12)
    encrypted_file = ContentFile(container_encrypt)
    encrypted_file.name = file.name  # esto será el nombre que Django guarda como filename

    file_instance = File(
        company=getattr(user, 'company', None), 
        branch=getattr(user, 'branch', None), 
        folder=dataFile.get("folder"),           # need be a object folder valid
        key=key,
        name=name,
        description=dataFile.get("description", ""),
        anchored = dataFile.get("anchored", False),
        upload_user=user
    )


    return {"success": True, "message": "files.message.file-upload-with-success", "file_id": file_instance.id}


def get_user_accessible_files(user):
    # Carpetas a las que tiene permiso directo
    permitted_folders = Folder.objects.filter(
        models.Q(permissions__user=user) | models.Q(permissions__role=user.role)
    ).distinct()

    # Archivos dentro de esas carpetas
    files = File.objects.filter(folder__in=permitted_folders)
    return files

def get_folder_tree_accessible(user, folder):
    # Carpetas hijo que hereden permisos
    permitted_folders = Folder.objects.filter(
        models.Q(permissions__user=user) | models.Q(permissions__role=user.role)
    )

    return folder.get_descendants().filter(id__in=permitted_folders)