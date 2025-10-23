'''
this both functions are for calculate the space that the user have in the server and if can upload more 
files to his count. If the user is use the software in desktop, the can upload all the files that need unlimited.
'''
from django.db.models import Sum
from django.http import FileResponse
from django.utils import timezone
from ..models import Folder, FolderPermission, File
from cryptography.fernet import Fernet #this is for encrypt the file
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
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


#-----------------------permissions-----------------------
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

def format_size(size_bytes):
    #this functions is for format the size of the files in B, KB, MB, GB, TB
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

def get_the_object_folder(user, folder_id):
    #if the proggramer send information of the parent, we will to get the object folder
    parent_folder=None
    if isinstance(folder_id, (int, str)):
        # if parent_folder is send as empty, None, or text type "null" → that is equal to treat as without parent
        if not folder_id or str(folder_id).strip() == "" or str(folder_id).lower() == "null":
            folder_id = None
        else:
            try:
                parent_folder = Folder.objects.get(id=folder_id)
            except Folder.DoesNotExist:
                parent_folder = None

    #we will see if the user have the permissions for create a new folder in the root or in the folder
    if parent_folder:
        try:
            permission = FolderPermission.objects.get(folder=parent_folder, user=user)
        except FolderPermission.DoesNotExist:
            return {"success": False, "message": "error.unauthorized", "error": "User does not have permission to create in this folder"}

        if not (permission.can_write or permission.can_add_members):
            return {"success": False, "message": "error.unauthorized", "error": "User cannot create subfolders"}
        else:
            return {"success": True, "message": "", "error":"", "answer": parent_folder}
        

    return {"success": True, "message": "", "error":"", "answer": parent_folder}




#-----------------------upload and download files-----------------------
def upload_file(user, parent_folder, dataFile) -> dict:
    file = dataFile.get("file")
    name = dataFile.get("name")

    if not file:
        return {"success": False, "message": "files.message.not-exist-file", "error": "You need upload a file"}
    
    if not name or not name.strip():
        name = file.name

    if not can_upload(user, file.size):
        return {"success": False, "message": "file.message.not-can-upload-the-file-because-not-have-memory", "error": "insufficient memory"}

    parent_folder_obj = get_the_object_folder(user, parent_folder)
    if not parent_folder_obj.get("success", False):
        return {"success": False, "message": parent_folder_obj.get("message"), "error": parent_folder_obj.get("error")}

    parent_folder = parent_folder_obj.get("answer")

    #this is for avoid that exist two files with the same name in the same folder
    original_name = name
    counter = 1
    while File.objects.filter(folder=parent_folder, name=name).exists():
        if '.' in original_name:
            base, ext = original_name.rsplit('.', 1)
            name = f"{base} ({counter}).{ext}"
        else:
            name = f"{original_name} ({counter})"
        counter += 1

    #create the instance of the file
    file_instance = File(
        company=getattr(user, 'company', None),
        branch=getattr(user, 'branch', None),
        folder=parent_folder,
        name=name,
        description=dataFile.get("description", ""),
        anchored=Plus.to_bool(dataFile.get("anchored", False)),
        upload_user=user
    )

    # save the file temporarily in memory
    temp_file_content = file.read()
    temp_file = ContentFile(temp_file_content)
    temp_file.name = file.name
    file_instance.file.save(file.name, temp_file, save=False)
    file_instance.save()

    # create the miniature (thumbnail)
    from .utils import generate_thumbnail_for_file
    thumb_url = generate_thumbnail_for_file(file_instance)
    if thumb_url:
        rel_path = thumb_url.replace(settings.MEDIA_URL, "")
        file_instance.thumbnail.name = rel_path
        file_instance.save(update_fields=["thumbnail"])

    # save the path of the temporary file before encrypting
    temp_file_path = file_instance.file.path

    # encrypt the file and overwrite the saved file
    container_encrypt = f.encrypt(temp_file_content)
    encrypted_file = ContentFile(container_encrypt)
    encrypted_file.name = file.name
    file_instance.file.save(file.name, encrypted_file, save=True)  # Overwrite the temporary file

    # Delete original temporary file
    if os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
        except Exception:
            pass

    # Generate full path
    def get_full_folder_path(folder):
        path = []
        while folder:
            path.insert(0, folder.name)
            folder = folder.parent
        return "/" + "/".join(path)

    file_path = get_full_folder_path(file_instance.folder) + "/" + file_instance.name

    return {
        "success": True,
        "message": "files.message.file-upload-with-success",
        "file_id": file_instance.id,
        "file_path": file_path
    }

def download_file(user, file_id):
    try:
        file_instance = File.objects.get(id=file_id)
    except File.DoesNotExist:
        return None, None
    
    # Verificar permisos
    if not has_folder_permission(user, file_instance.folder, "read"):
        return None, None

    # Ruta al archivo encriptado
    file_path = file_instance.file.path
    if not os.path.exists(file_path):
        return None, None

    # Leer y desencriptar
    with open(file_path, "rb") as f_encrypted:
        encrypted_content = f_encrypted.read()
    decrypted_content = f.decrypt(encrypted_content)

    return decrypted_content, file_instance




#-----------------------get files-----------------------
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

def get_folder_files(user, folder=None, query=None, page=1, per_page=10) -> dict:
    """
    Get the files of a folder with pagination.
    If folder is None, get anchored files (True) that the user can read and belong to their company.
    """
    try:
        # Convert folder ID to object if necessary
        if folder == "" or folder is None:
            folder = None
        elif isinstance(folder, int) or (isinstance(folder, str) and folder.isdigit()):
            folder = Folder.objects.get(id=int(folder))
        else:
            folder = None

        # Si se proporcionó una carpeta, verificar permisos
        if folder and not has_folder_permission(user, folder, "read"):
            return {
                "success": False,
                "message": "error.unauthorized",
                "answer": [],
                "error": "the user does not have permission to access this folder"
            }

        # Si no hay carpeta, obtener los archivos anclados que el usuario puede leer
        if folder is None:
            files_qs = File.objects.filter(
                anchored=True,
                company=getattr(user, "company", None)
            )

            # Filtrar por permisos (solo los que el usuario puede leer)
            readable_files = []
            for f in files_qs:
                if f.folder is None or has_folder_permission(user, f.folder, "read"):
                    readable_files.append(f.id)

            files_qs = File.objects.filter(id__in=readable_files)

        else:
            # Si hay carpeta, obtener sus archivos normalmente
            files_qs = File.objects.filter(folder=folder)

        # Aplicar filtro de búsqueda (query)
        if query and query.strip():
            files_qs = files_qs.filter(name__icontains=query.strip())

        # Ordenar por fecha descendente
        files_qs = files_qs.order_by('-uploaded_at')

        # Paginación
        paginator = Paginator(files_qs, per_page)
        page_obj = paginator.get_page(page)

        data = {
            "files": [
                {
                    "id": f.id,
                    "name": f.name,
                    "description": f.description,
                    "anchored": f.anchored,
                    "size": f.size,
                    "uploaded_at": Plus.format_date_to_text(
                        Plus.convert_from_utc(f.uploaded_at, user.timezone),
                        user.language,
                        2
                    ),
                    "thumbnail": f.thumbnail.url if f.thumbnail else None,
                    "file_url": f.file.url if f.file else None,
                    "username": f.upload_user.username if f.upload_user else None,
                    "avatar": (
                        f.upload_user.avatar.url
                        if f.upload_user and f.upload_user.avatar
                        else '/static/img/employees-select.webp'
                    )
                }
                for f in page_obj.object_list
            ],
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_files": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }

        return {"success": True, "message": "", "answer": data, "error": ""}

    except Folder.DoesNotExist:
        return {"success": False, "message": "error.folder-not-found", "answer": [], "error": "Folder not found"}
    except Exception as e:
        return {"success": False, "message": "error.internal-error", "answer": [], "error": str(e)}


def get_file_detail(user, file_id) -> dict:
    if not file_id:
        return {
            "success": False,
            "message": "error.file-not-provided",
            "error": "File ID was not provided"
        }

    try:
        file_obj = File.objects.select_related(
            'folder', 'upload_user', 'company', 'branch'
        ).get(id=file_id)
    except ObjectDoesNotExist:
        return {
            "success": False,
            "message": "error.file-not-found",
            "error": f"File with ID {file_id} was not found"
        }

    # ✅ Verificar si el usuario es el dueño del archivo o de la carpeta
    is_owner = file_obj.upload_user == user or file_obj.folder.creator_user == user

    # ✅ Verificar si tiene permisos de lectura en la carpeta
    has_permission = FolderPermission.objects.filter(
        folder=file_obj.folder,
        user=user,
        can_read=True
    ).exists()

    if not is_owner and not has_permission:
        return {
            "success": False,
            "message": "error.permission-denied",
            "error": "User does not have permission to view this file"
        }

    # ✅ Si todo va bien, devolver la información del archivo
    file_data = {
        "id": file_obj.id,
        "name": file_obj.name,
        "description": file_obj.description or "",
        "url": file_obj.url,
        "anchored": file_obj.anchored,
        "size": format_size(file_obj.size),
        "thumbnail": file_obj.thumbnail.url if file_obj.thumbnail else None,
        #"uploaded_at": Plus.format_date_to_text(Plus.convert_to_utc(file_obj.uploaded_at, user.timezone), user.language, 2),
        "uploaded_at": Plus.format_date_to_text(
            Plus.convert_from_utc(file_obj.uploaded_at, user.timezone),
            user.language,
            1
        ),
        "upload_user": {
            "id": file_obj.upload_user.id if file_obj.upload_user else None,
            "name": str(file_obj.upload_user) if file_obj.upload_user else None,
        },
        "folder": {
            "id": file_obj.folder.id,
            "name": file_obj.folder.name,
        }
    }

    return {
        "success": True,
        "message": "success.file-found",
        "answer": file_data,
        "error": '',
    }

def update_file(user, file_id, dataFile) -> dict:
    """
    Actualiza los datos básicos de un archivo (nombre, descripción, anchored)
    """
    try:
        # Buscar el archivo
        file_instance = File.objects.filter(id=file_id).first()
        if not file_instance:
            return {"success": False, "message": "files.message.file-not-found", "error": "File not found"}

        # Verificar que el usuario tenga permiso
        # (Ejemplo básico: debe ser el usuario que lo subió o tener rol administrador)
        if file_instance.upload_user != user and not user.is_staff:
            return {"success": False, "message": "files.message.permission-denied", "error": "Permission denied"}

        # Obtener nuevos valores
        new_name = dataFile.get("name", file_instance.name)
        new_description = dataFile.get("description", file_instance.description)
        new_anchored = Plus.to_bool(dataFile.get("anchored", False))

        # Si el nombre cambió, verificar que no haya duplicados en la misma carpeta
        if new_name != file_instance.name:
            original_name = new_name
            counter = 1
            while File.objects.filter(folder=file_instance.folder, name=new_name).exclude(id=file_id).exists():
                if '.' in original_name:
                    base, ext = original_name.rsplit('.', 1)
                    new_name = f"{base} ({counter}).{ext}"
                else:
                    new_name = f"{original_name} ({counter})"
                counter += 1

        # Actualizar campos
        file_instance.name = new_name
        file_instance.description = new_description
        file_instance.anchored = new_anchored
        file_instance.save(update_fields=["name", "description", "anchored"])

        # Generar la nueva ruta completa del archivo
        def get_full_folder_path(folder):
            path = []
            while folder:
                path.insert(0, folder.name)
                folder = folder.parent
            return "/" + "/".join(path)

        file_path = get_full_folder_path(file_instance.folder) + "/" + file_instance.name

        return {
            "success": True,
            "message": "files.message.file-updated-successfully",
            "error": "",
        }

    except Exception as e:
        return {"success": False, "message": "files.message.error-updating-file", "error": str(e)} 

#==================================folders=========================
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

    #if the proggramer send information of the parent, we will to get the object folder and 
    # we will see if the user have the permissions for create a new folder in the root or in the folder
    parent_folder_obj = get_the_object_folder(user, parent_folder)
    if not parent_folder_obj.get("success", False):
        return {"success": parent_folder_obj.get("success"), "message": parent_folder_obj.get("message"), "error": parent_folder_obj.get("error")}

    parent_folder=parent_folder_obj.get("answer", None) #get the object folder



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
        return {"success": False, "message": "error.failed_save", "answer":"", "error": f"Error when we create the folder {str(e)}"}

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

def update_folder(user, folder_id, data=None):
    """
    Update an existing folder if the user has permissions to edit it.

    Parameters:
        - user: User requesting the update.
        - folder_id: ID of the folder to update.
        - data: dict with updated fields. Example: {"name": "Updated folder", "color": "#FFAA00"}
    """

    if not folder_id:
        return {"success": False, "answer": "", "message": "error.folder-not-provided", "error": "Folder ID was not provided"}

    if data is None or not isinstance(data, dict):
        return {"success": False, "answer": "", "message": "error.invalid-data", "error": "The provided data is invalid or empty"}

    # --- Get the folder instance ---
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {"success": False, "answer": "", "message": "error.not-found", "error": f"The folder with id {folder_id} does not exist"}

    # --- Verify permissions ---
    try:
        permission = FolderPermission.objects.get(folder=folder, user=user)
    except FolderPermission.DoesNotExist:
        return {"success": False, "answer": "", "message": "error.unauthorized", "error": "The user does not have permissions for this folder"}

    if not permission.can_write:
        return {"success": False, "answer": "", "message": "error.unauthorized", "error": "The user does not have edit permissions on this folder"}

    # --- Update folder fields ---
    try:
        folder.name = data["name"]
        folder.color = data["color"]
        folder.save()


    except Exception as e:
        return {"success": False, "answer": "", "message": "error.failed_update", "error": str(e)}

    # --- Response ---
    return {
        "success": True,
        "message": "success.folder-updated",
        "answer": {
            "id": folder.id,
            "name": folder.name,
            "color": folder.color,
            "company": folder.company.company_name if folder.company else None,
            "branch": folder.branch.name_branch if folder.branch else None,
            "parent": folder.parent.id if folder.parent else None,
            "creator": folder.creator_user.username if folder.creator_user else None,
            "updated_at": timezone.now(),
        },
        "error": None,
    }

def get_folders(user, folder=None, query=None):
    """
    Get folders accessible by the user.
    
    - If 'folder' is provided, get its immediate subfolders.
    - If 'folder' is None, get root folders (no parent).
    - Optionally filter by 'query' in the folder name.
    """
    # Base queryset
    if folder:
        # If folder is an ID, convert to object
        if isinstance(folder, int):
            folder = Folder.objects.get(id=folder)
        folders_qs = Folder.objects.filter(parent=folder)
    else:
        folders_qs = Folder.objects.filter(parent=None)
    
    # Filter by company and branch if provided
    company=user.company
    branch=user.branch
    if company:
        folders_qs = folders_qs.filter(company=company)
    if branch:
        folders_qs = folders_qs.filter(branch=branch)
    
    # Apply query filter if provided
    if query and query.strip():
        folders_qs = folders_qs.filter(name__icontains=query.strip())
    
    # Filter by user permissions
    accessible_folders = [
        f for f in folders_qs
        if has_folder_permission(user, f, "read")
    ]
    
    # Prepare response
    data = [
        {
            "id": f.id,
            "name": f.name,
            "color": f.color,
            "created_at": Plus.format_date_to_text(
                Plus.convert_from_utc(f.created_at, user.timezone),
                user.language,
                2
            ),
        }
        for f in accessible_folders
    ]
    
    return {"success": True, "message": "", "answer": data, "error": ""}

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
        "company": folder.company.company_name if folder.company else None,
        "branch": folder.branch.name_branch if folder.branch else None,
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

#--------------------donwload the folder as zip--------------------
import os
import tempfile
import zipfile
def download_folder(user, folder_id):
    import tempfile, zipfile, os

    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return False

    if not has_folder_permission(user, folder, "read"):
        return False

    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_files_to_delete = []  # 👈 aquí guardaremos los archivos temporales

    try:
        with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            def add_folder_to_zip(current_folder, current_path=""):
                files = File.objects.filter(folder=current_folder)
                for file_instance in files:
                    file_path = file_instance.file.path
                    if not os.path.exists(file_path):
                        continue

                    with open(file_path, "rb") as f_encrypted:
                        encrypted_content = f_encrypted.read()
                    decrypted_content = f.decrypt(encrypted_content)

                    zip_path = os.path.join(current_path, file_instance.name)

                    # Guardamos temporalmente el archivo desencriptado
                    temp_file = tempfile.NamedTemporaryFile(delete=False)
                    temp_file.write(decrypted_content)
                    temp_file.flush()
                    temp_file.close()

                    # Añadir al ZIP
                    zipf.write(temp_file.name, arcname=zip_path)
                    temp_files_to_delete.append(temp_file.name)

                for subfolder in current_folder.subfolders.all():
                    sub_path = os.path.join(current_path, subfolder.name)
                    add_folder_to_zip(subfolder, sub_path)

            add_folder_to_zip(folder)

        # ✅ Ahora que el ZIP está cerrado, ya podemos borrar los archivos temporales
        for fpath in temp_files_to_delete:
            try:
                os.remove(fpath)
            except Exception:
                pass

        return temp_zip, folder.name

    finally:
        pass

#--------------------delete the folder and all his content--------------------
from django.db import transaction
def delete_folder(user, folder_id):
    """
    Delete a folder and all its subfolders and files recursively.
    Requires that the user has permission to delete the folder.
    """

    if not folder_id:
        return {
            "success": False,
            "message": "error.folder-not-provided",
            "error": "Folder ID was not provided"
        }

    # --- Get folder ---
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {
            "success": False,
            "message": "error.not-found",
            "error": f"The folder with id {folder_id} does not exist"
        }

    # --- Check permissions ---
    try:
        permission = FolderPermission.objects.get(folder=folder, user=user)
    except FolderPermission.DoesNotExist:
        return {
            "success": False,
            "message": "error.unauthorized",
            "error": "The user does not have permissions for this folder"
        }

    if not (permission.can_write or permission.can_delete):
        return {
            "success": False,
            "message": "error.unauthorized",
            "error": "The user does not have permission to delete this folder"
        }

    # --- Recursive deletion ---
    try:
        with transaction.atomic():
            deleted_count = _delete_folder_recursive(folder)
    except Exception as e:
        return {
            "success": False,
            "message": "error.failed-deletion",
            "error": str(e)
        }

    # --- Response ---
    return {
        "success": True,
        "message": "success.folder-deleted",
        "answer": {
            "deleted_folders": deleted_count["folders"],
            "deleted_files": deleted_count["files"],
            "deleted_at": timezone.now(),
        },
        "error": None,
    }

def _delete_folder_recursive(folder):
    """
    Recursively delete all subfolders and files in a folder.
    Deletes both database records and physical files.
    Returns a dict with the count of deleted folders and files.
    """

    folders_deleted = 0
    files_deleted = 0

    # delete the files that exist in this folder
    for f in folder.files.all():
        # delete physical file
        if f.file and os.path.exists(f.file.path):
            try:
                os.remove(f.file.path)
            except Exception:
                pass

        # delete thumbnail
        if f.thumbnail and os.path.exists(f.thumbnail.path):
            try:
                os.remove(f.thumbnail.path)
            except Exception:
                pass

        # Finally delete the database record
        f.delete()
        files_deleted += 1

    # Delete subfolders recursively
    for subfolder in folder.subfolders.all():
        result = _delete_folder_recursive(subfolder)
        folders_deleted += result["folders"]
        files_deleted += result["files"]

    # Finally delete the current folder
    folder.delete()
    folders_deleted += 1

    return {"folders": folders_deleted, "files": files_deleted}