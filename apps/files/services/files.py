'''
this both functions are for calculate the space that the user have in the server and if can upload more 
files to his count. If the user is use the software in desktop, the can upload all the files that need unlimited.
'''
from django.db.models import Sum
from ..models import Folder, FolderPermission, File
from cryptography.fernet import Fernet #this is for encrypt the file
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
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
    file = dataFile.get("file")
    name = dataFile.get("name")

    #now we will see if the file have all the information that need for save in the database else return a message for show in the frontend
    if not file:
        return {"success": False, "message": "files.message.not-exist-file", "error": "You need upload a file"}
    
    if not name or not name.strip():
        if file:
            name = file.name
        else:
            return {"success": False, "message": "files.message.not-exist-file", "error": "You need upload a file"}

    if not can_upload(user, file.size):
        return {"success": False, "message": "file.message.not-can-upload-the-file-because-not-have-memory", "error": "insufficient memory"}

    #Now first we save a temporary version of the file to be able to create the thumbnail
    key = get_random_string(12)

    file_instance = File(
        company=getattr(user, 'company', None), 
        branch=getattr(user, 'branch', None), 
        folder=dataFile.get("folder"),
        key=key,
        name=name,
        description=dataFile.get("description", ""),
        anchored=dataFile.get("anchored", False),
        upload_user=user
    )

    # We assign the file temporarily (still unencrypted beacuse we required to have an ID before creating the thumbnail) 
    file_instance.file.save(file.name, file, save=False)
    file_instance.save()  

    #now make the miniature before of encrypt the file
    from .utils import generate_thumbnail_for_file
    thumb_url = generate_thumbnail_for_file(file_instance)
    if thumb_url:
        # Convert URL to relative path and assign it
        rel_path = thumb_url.replace(settings.MEDIA_URL, "")
        file_instance.thumbnail.name = rel_path
        file_instance.save(update_fields=["thumbnail"])

    #Now we read and encrypt the original file
    file.seek(0)
    container = file.read()
    container_encrypt = f.encrypt(container)

    # We replace the file with the encrypted version
    encrypted_file = ContentFile(container_encrypt)
    encrypted_file.name = file.name
    file_instance.file.save(file.name, encrypted_file, save=True)

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

def get_folder_files(folder, page=1, per_page=10):
    """
    get the files of a folder with a pagination.
    return the data of the page with his data 
    """
    # If folder is an ID, we convert it to an object
    if isinstance(folder, int):
        folder = Folder.objects.get(id=folder)

    files_qs = File.objects.filter(folder=folder).order_by('-uploaded_at')

    paginator = Paginator(files_qs, per_page)
    page_obj = paginator.get_page(page)

    data = {
        "files": [
            {
                "id": f.id,
                "name": f.name,
                "description": f.description,
                "size": f.size,
                "uploaded_at": f.uploaded_at,
                "thumbnail": f.thumbnail.url if f.thumbnail else None,
                "file_url": f.file.url if f.file else None,
            }
            for f in page_obj.object_list
        ],
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_files": paginator.count,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    }

    return data