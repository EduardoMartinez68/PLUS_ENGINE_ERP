'''
this both functions are for calculate the space that the user have in the server and if can upload more 
files to his count. If the user is use the software in desktop, the can upload all the files that need unlimited.
'''
from django.db.models import Sum
from django.utils import timezone
from ..models import Folder, FolderPermission, File
from cryptography.fernet import Fernet #this is for encrypt the file
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
import os
from ..plus_wrapper import Plus
from dotenv import load_dotenv
load_dotenv()

#get the type of software 
TYPE_VERSION = os.environ.get('TYPE_VERSION')

#get the key of encrypt that is in our file .env
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY').encode()
f = Fernet(FIELD_ENCRYPTION_KEY)

def has_folder_permission(user, folder, action: str) -> bool:
    """
    Checks if the user has permission on a folder to perform a specific action.
    :param user: CustomUser
    :param folder: Folder o ID
    :param action: string like 'read', 'write', 'delete', 'upload_file', etc.
    :return: bool
    """
    if not user or not folder:
        return False

    #if the programmer send a id we will to get the object folder 
    if isinstance(folder, int):
        try:
            folder = Folder.objects.get(id=folder)
        except Folder.DoesNotExist:
            return False

    # If the user is the creator of the folder, he has all permissions
    if folder.creator_user == user:
        return True

    # Attempt to obtain the registered permission for the user
    try:
        permission = FolderPermission.objects.get(folder=folder, user=user)
    except FolderPermission.DoesNotExist:
        return False

    # Mapping actions to boolean fields
    action_map = {
        "read": permission.can_read,
        "copy": permission.can_copy,
        "write": permission.can_write,
        "delete": permission.can_delete,
        "upload_file": permission.can_upload_file,
        "update_file": permission.can_update_file,
        "copy_file": permission.can_copy_file,
        "delete_file": permission.can_delete_file,
        "change_permission": permission.can_change_the_permission,
        "add_members": permission.can_add_members,
        "delete_members": permission.can_delete_members,
    }

    return action_map.get(action, False)

def user_storage_used(user)->bool:
    return File.objects.filter(upload_user=user).aggregate(total=Sum('size'))['total'] or 0

def can_upload(user, filesize)->bool:
    limit = get_limit_of_the_user() * 1024 * 1024 * 1024  # 1 GiB
    return user_storage_used(user) + filesize <= limit

def get_limit_of_the_user()->int:
    if TYPE_VERSION=='DESKTOP':
        return True
    

    #here we will see the pack that have the user in the subscription and return the size of his space
    #pack 1==1 GiB
    #pack 2==5 GiB
    return 1

def upload_file(user, dataFile)->list:
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


def get_user_accessible_files(user)->list:
    # Carpetas a las que tiene permiso directo
    permitted_folders = Folder.objects.filter(
        models.Q(permissions__user=user) | models.Q(permissions__role=user.role)
    ).distinct()

    # Archivos dentro de esas carpetas
    files = File.objects.filter(folder__in=permitted_folders)
    return files

def get_folder_tree_accessible(user, folder)->list:
    # Carpetas hijo que hereden permisos
    permitted_folders = Folder.objects.filter(
        models.Q(permissions__user=user) | models.Q(permissions__role=user.role)
    )

    return folder.get_descendants().filter(id__in=permitted_folders)

def get_folder_files(user, folder, page=1, per_page=10)->list:
    """
    get the files of a folder with a pagination.
    return the data of the page with his data 
    """

    # If folder is an ID, we convert it to an object
    if isinstance(folder, int):
        folder = Folder.objects.get(id=folder)


    #now before of get the files of the folder we need see if the user have the permission for this
    if not has_folder_permission(user, folder, "read"):
        return {"success": False, "message": "file.message.not-can-upload-the-file-because-not-have-memory", "error": "insufficient memory"}

    #if the user have the permission for see the files of this folder now we will get the files
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

def get_root_folders(user, company=None, branch=None):
    """
    return all the folder that the user have permission of see in the room and that not have parent 
    """
    folders_qs = Folder.objects.filter(parent=None)

    if company:
        folders_qs = folders_qs.filter(company=company)
    if branch:
        folders_qs = folders_qs.filter(branch=branch)

    # filter by permission of the user
    accessible_folders = [
        folder for folder in folders_qs
        if has_folder_permission(user, folder, "read")
    ]

    data = [
        {
            "id": f.id,
            "name": f.name,
            "color": f.color,
            "created_at": Plus.format_date_to_text(Plus.convert_from_utc(f.created_at, user.timezone), user.language, 2),
            "creator": f.creator_user.username if f.creator_user else None
        }
        for f in accessible_folders
    ]

    return {"success": True, "message": "", "answer": data, "error": "insufficient memory"}

def get_folder_detail(user, folder_id):
    """
    return all the information of the folder (subfolder, files, permissions)
    only if the user have the permissions for see his information.
    """

    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {"success": False, "message": "", "error": "The folder not found."}

    #here we will see if the user have the permission of see the information of the folder
    try:
        permission = FolderPermission.objects.get(folder=folder, user=user)
    except FolderPermission.DoesNotExist:
        return {"success": False, "message": "", "error": "The user not have the permissions"}


    # if the user not can read the information of the folder return a message
    if not permission.can_write:
        return {"success": False, "message": "", "error": "The user not have the permissions"}

    #get the total of the subfolders and the files that exist in the folder
    total_folders = folder.subfolders.count()
    total_fieles=folder.files.count()

    # Información general del folder
    folder_data = {
        "id": folder.id,
        "name": folder.name,
        "color": folder.color,
        "company": folder.company.name if folder.company else None,
        "branch": folder.branch.name if folder.branch else None,
        "created_at": folder.created_at,
        "creator": folder.creator_user.username if folder.creator_user else None,
        "parent": folder.parent.id if folder.parent else None,
        "permissions": {
            "can_read": permission.can_read,
            "can_copy": permission.can_copy,
            "can_write": permission.can_write,
            "can_delete": permission.can_delete,
            "can_upload_file": permission.can_upload_file,
            "can_move_file": permission.can_move_file,
            "can_update_file": permission.can_update_file,
            "can_copy_file": permission.can_copy_file,
            "can_delete_file": permission.can_delete_file,
            "can_change_the_permission": permission.can_change_the_permission,
            "can_add_members": permission.can_add_members,
            "can_delete_members": permission.can_delete_members,
        },
        "total_fieles": total_fieles,
        "total_folders": total_folders
    }

    return {
        "success": True,
        "message": "Information get with success",
        "answer": folder_data,
        "error": None,
    }

def create_folder(user, parent_folder=None, data=None):
    """
    Make a new folder if the user have the permissions for this.
    
    Parameters:
        - user: user that would like create the folder
        - parent_folder: instance of Folder or None (if root)
        - data: dict with the information of the form
                 example: {"name": "New folder", "color": "#FFAA00"}
    """

    if data is None:
        return {"success": False, "message": "error.not-send-information-to-the-server", "error": "Not exist the data"}

    #we will see if the user have the permissions for create a new folder in the root or in the folder
    if parent_folder:
        try:
            permission = FolderPermission.objects.get(folder=parent_folder, user=user)
        except FolderPermission.DoesNotExist:
            return {"success": False, "message": "error.unauthorized", "error": "The user not have the permissions for create a new folder in the path of the father"}

        if not (permission.can_write or permission.can_add_members):
            return {"success": False, "message": "error.unauthorized", "error": "The user not have permissions for create subfolders"}

    #if the user have all the permissions for this, now we will to create the new folder
    try:
        new_folder = Folder.objects.create(
            company=user.company,
            branch=user.branch,
            name=data.get("name", "new folder"),
            color=data.get("color", "#3A7BD5"),
            parent=parent_folder,
            created_at=timezone.now(),
            creator_user=user
        )
    except Exception as e:
        return {"success": False, "message": "error.failed_save", "error": f"Error when we create the folder {str(e)}"}

    #now we will to create the permissions for the creator
    FolderPermission.objects.create(
        folder=new_folder,
        user=user,
        can_read=True,
        can_copy=True,
        can_write=True,
        can_delete=True,
        can_upload_file=True,
        can_move_file=True,
        can_update_file=True,
        can_copy_file=True,
        can_delete_file=True,
        can_change_the_permission=True,
        can_add_members=True,
        can_delete_members=True,
    )

    return {
        "success": True,
        "message": "",
        "answer": {
            "id": new_folder.id,
            "name": new_folder.name,
            "color": new_folder.color,
            "company": new_folder.company.company_name if new_folder.company else None,
            "branch": new_folder.branch.name_branch if new_folder.branch else None,
            "created_at": new_folder.created_at,
            "parent": new_folder.parent.id if new_folder.parent else None,
            "creator": user.username,
        },
        "error": 'the folder was create with success',
    }
