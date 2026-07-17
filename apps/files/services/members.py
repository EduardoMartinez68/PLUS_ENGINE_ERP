from ..models import Folder, FolderPermission, File
from ..plus_wrapper import Plus
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from core.models import CustomUser 
from .permissions import has_folder_permission

def get_members_of_folder(user, folder_id, search=None):
    """
    get all the member of a folder with his permissions.
    If 'search' is provided, filter the results by name, email or username.
    """
    if not folder_id or str(folder_id).strip() == "":
        return {
            "success": False,
            "message": "files.message.folder-id-invalid",
            "error": "Folder ID is empty or invalid"
        }

    # 1️⃣ we will see that the folder exist 
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.folder-not-found",
            "error": f"The folder with id {folder_id} does not exist"
        }

    # 2️⃣ we will see if the user have permission to view members of the folder
    if not has_folder_permission(user, folder, 'can_see_members'):
        return {
            "success": False,
            "message": "files.message.no-permission-view-members",
            "answer":[],
            "error": "User does not have permission to view members of this folder"
        }

    # 3️⃣ we will see the permissions of users with access to the folder
    permissions = FolderPermission.objects.filter(folder=folder).select_related('user')

    # 4️⃣ Filter by search (if provided)
    if search:
        search = search.strip().lower()
        permissions = permissions.filter(
            Q(user__username__icontains=search) |
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search)
        )

    # 5️⃣ Build members list
    members_list = []
    for perm in permissions:
        member = perm.user
        if not member:
            continue  # Skip if user does not exist
        

        #construct the member dict with permissions
        members_list.append({
            "id": member.id,
            "username": member.username,
            "member_name": member.name,
            "email": member.email,
            "avatar": member.avatar.url if member.avatar else None,
        })

    return {
        "success": True,
        "answer": members_list,
        "message": "files.message.members-retrieved",
        "error": None
    }


def delete_member_of_folder(user, folder_id, member_id):
    """
    Delete a member from a folder.
    """
    if not folder_id or str(folder_id).strip() == "":
        return {
            "success": False,
            "message": "files.error.not-exist-member",
            "error": "Folder ID is empty or invalid"
        }

    # 1️⃣ we will see that the folder exist 
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.folder-id-not-exit",
            "error": f"The folder with id {folder_id} does not exist"
        }

    # 2️⃣ we will see if the user have permission to delete members of the folder
    if not has_folder_permission(user, folder, "delete_members"):
        return {
            "success": False,
            "answer": "",
            "message": "files.error.permission-denied",
            "error": f"User {user.name} has no permission to add members to folder {folder_id}."
        }

    # 3️⃣ avoid delete to the creator of the folder
    if str(folder.creator_user.id) == str(member_id):
        return {
            "success": False,
            "message": "files.error.cannot-delete-creator-folder",
            "error": "You cannot delete the creator of this folder"
        }
    
    # 4️⃣ we will try to delete the member
    try:
        permission = FolderPermission.objects.get(folder=folder, user__id=member_id)
        permission.delete()
        return {
            "success": True,
            "answer": "",
            "message": "files.title.member-folder-deleted",
            "error": f"Member with id {member_id} deleted from folder {folder_id}"
        }
    except FolderPermission.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.member-not-found",
            "error": f"Member with id {member_id} does not exist in folder {folder_id}"
        }
    
def add_member_to_folder(user, folder_id, member_id, data):
    try:
        folder = Folder.objects.get(id=folder_id)
    except ObjectDoesNotExist:
        return {
            "success": False,
            "answer": "",
            "message": "files.error.folder-not-found",
            "error": f"Folder with id {folder_id} not found."
        }

    # ✅ if the user not is the creator of the folder we will see if the user have the permissions that need
    if not has_folder_permission(user, folder, "add_members"):
        return {
            "success": False,
            "answer": "",
            "message": "files.error.permission-denied",
            "error": f"User {user.name} has no permission to add members to folder {folder_id}."
        }

    # ✅ we will see if the new member exist
    try:
        member = CustomUser.objects.get(id=member_id)
    except ObjectDoesNotExist:
        return {
            "success": False,
            "answer": "",
            "message": "files.error.member-not-found",
            "error": f"Member with id {member_id} not found."
        }

    # ✅ check that the new member is in the same company
    if member.company_id != folder.company_id:
        return {
            "success": False,
            "answer": "",
            "message": "files.error.member-not-in-company",
            "error": f"Member {member_id} does not belong to company {folder.company_id}."
        }

    # ✅ we will see if already exists this user in the folder
    if FolderPermission.objects.filter(folder=folder, user=member).exists():
        return {
            "success": False,
            "answer": "",
            "message": "files.error.member-already-added",
            "error": f"Member {member_id} is already in folder {folder_id}."
        }



    # ✅ add a new member with the permissions that the user send from the frontend
    FolderPermission.objects.create(
        folder=folder,
        user=member,

        can_see_folder=True,
        can_edit_folder=Plus.to_bool(data.get("can_edit_folder", False)),
        can_delete_folder=Plus.to_bool(data.get("can_delete_folder", False)),
        can_download_folder=Plus.to_bool(data.get("can_download_folder", False)),
        can_add_subfolder=Plus.to_bool(data.get("can_add_subfolder", False)),

        can_see_the_files=Plus.to_bool(data.get("can_see_the_files", True)),
        can_upload_file=Plus.to_bool(data.get("can_upload_file", False)),
        can_move_file=Plus.to_bool(data.get("can_move_file", False)),
        can_update_file=Plus.to_bool(data.get("can_update_file", False)),
        can_copy_file=Plus.to_bool(data.get("can_copy_file", False)),
        can_delete_file=Plus.to_bool(data.get("can_delete_file", False)),
        can_see_file=Plus.to_bool(data.get("can_see_file", True)),
        can_download_file=Plus.to_bool(data.get("can_download_file", False)),

        can_change_the_permission=Plus.to_bool(data.get("can_change_the_permission", False)),
        can_add_members=Plus.to_bool(data.get("can_add_members", False)),
        can_delete_members=Plus.to_bool(data.get("can_delete_members", False)),
        can_see_members=Plus.to_bool(data.get("can_see_members", False))
    )

    return {
        "success": True,
        "answer": "",
        "message": "files.title.member-folder-added",
        "error": f"Member with id {member_id} added to folder {folder_id}"
    }


def get_member_permissions_in_folder(user, folder_id, member_id):
    """
    Obtiene todos los permisos de un miembro dentro de una carpeta específica.
    - user: usuario que realiza la consulta (se usa para validar permisos).
    - folder_id: ID de la carpeta donde se buscan los permisos.
    - member_id: ID del miembro cuyos permisos queremos obtener.
    """

    # 1️⃣ Validar que el folder_id sea válido
    if not folder_id or str(folder_id).strip() == "":
        return {
            "success": False,
            "message": "files.message.folder-id-invalid",
            "error": "Folder ID is empty or invalid"
        }

    # 2️⃣ Validar que el member_id sea válido
    if not member_id or str(member_id).strip() == "":
        return {
            "success": False,
            "message": "files.message.member-id-invalid",
            "error": "Member ID is empty or invalid"
        }

    # 3️⃣ Verificar que la carpeta exista
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.folder-not-found",
            "error": f"The folder with id {folder_id} does not exist"
        }

    # 4️⃣ Verificar que el usuario tenga permiso para ver los miembros
    if not has_folder_permission(user, folder, 'can_see_members'):
        return {
            "success": False,
            "message": "files.message.no-permission-view-members",
            "error": "User does not have permission to view members of this folder"
        }

    # 5️⃣ Verificar que el miembro exista
    try:
        member = CustomUser.objects.get(id=member_id)
    except CustomUser.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.member-not-found",
            "error": f"Member with id {member_id} not found"
        }

    # 6️⃣ Buscar el registro de permisos
    try:
        permission = FolderPermission.objects.get(folder=folder, user=member)
    except FolderPermission.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.permissions-not-found",
            "error": "This member does not have permissions in the specified folder"
        }

    # 7️⃣ Construir la respuesta con todos los permisos
    permissions_dict = {
        "can_see_folder": permission.can_see_folder,
        "can_edit_folder": permission.can_edit_folder,
        "can_delete_folder": permission.can_delete_folder,
        "can_download_folder": permission.can_download_folder,
        "can_add_subfolder": permission.can_add_subfolder,

        "can_see_the_files": permission.can_see_the_files,
        "can_upload_file": permission.can_upload_file,
        "can_move_file": permission.can_move_file,
        "can_update_file": permission.can_update_file,
        "can_copy_file": permission.can_copy_file,
        "can_delete_file": permission.can_delete_file,
        "can_see_file": permission.can_see_file,
        "can_download_file": permission.can_download_file,

        "can_change_the_permission": permission.can_change_the_permission,
        "can_see_members": permission.can_see_members,
        "can_add_members": permission.can_add_members,
        "can_delete_members": permission.can_delete_members,
    }

    # 8️⃣ Respuesta exitosa
    return {
        "success": True,
        "message": "files.message.member-permissions-retrieved",
        "username": member.username,
        "email": member.email,
        "name": member.name,
        "answer": permissions_dict,
        "error": None
    }

def update_member_permissions_in_folder(user, folder_id, member_id, data):
    """
    Actualiza los permisos de un miembro en un folder.
    - user: usuario que realiza la acción
    - folder_id: ID del folder
    - member_id: ID del miembro cuyos permisos se actualizarán
    - data: diccionario con los permisos a actualizar
    """
    # ✅ Validar y convertir a enteros
    try:
        folder_id = int(folder_id)
        member_id = int(member_id)
    except (TypeError, ValueError):
        return {
            "success": False,
            "answer": "",
            "message": "Invalid ID",
            "error": f"folder_id and member_id must be valid integers"
        }
    
    # 1️⃣ Verificar que la carpeta exista
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {
            "success": False,
            "answer": "",
            "message": "files.error.folder-not-found",
            "error": f"Folder with id {folder_id} not found."
        }

    # 2️⃣ Verificar permisos del usuario para editar miembros
    if not has_folder_permission(user, folder, "can_change_the_permission"):
        return {
            "success": False,
            "answer": "",
            "message": "files.error.permission-denied",
            "error": f"User {user.name} has no permission to edit member permissions in folder {folder_id}."
        }

    # 3️⃣ Verificar que el miembro exista
    try:
        member = CustomUser.objects.get(id=member_id)
    except CustomUser.DoesNotExist:
        return {
            "success": False,
            "answer": "",
            "message": "files.error.member-not-found",
            "error": f"Member with id {member_id} not found."
        }

    # 4️⃣ Verificar que el miembro tenga permisos existentes
    try:
        perm = FolderPermission.objects.get(folder=folder, user=member)
    except FolderPermission.DoesNotExist:
        return {
            "success": False,
            "answer": "",
            "message": "files.error.permissions-not-found",
            "error": f"Member {member_id} does not have permissions in folder {folder_id}."
        }

    # 5️⃣ Actualizar permisos
    perm.can_see_folder = Plus.to_bool(data.get("can_see_folder", False))
    perm.can_edit_folder = Plus.to_bool(data.get("can_edit_folder", False))
    perm.can_delete_folder = Plus.to_bool(data.get("can_delete_folder", False))
    perm.can_download_folder = Plus.to_bool(data.get("can_download_folder", False))
    perm.can_add_subfolder = Plus.to_bool(data.get("can_add_subfolder", False))

    perm.can_see_the_files = Plus.to_bool(data.get("can_see_the_files", False))
    perm.can_upload_file = Plus.to_bool(data.get("can_upload_file", False))
    perm.can_move_file = Plus.to_bool(data.get("can_move_file", False))
    perm.can_update_file = Plus.to_bool(data.get("can_update_file", False))
    perm.can_copy_file = Plus.to_bool(data.get("can_copy_file", False))
    perm.can_delete_file = Plus.to_bool(data.get("can_delete_file", False))
    perm.can_see_file = Plus.to_bool(data.get("can_see_file", False))
    perm.can_download_file = Plus.to_bool(data.get("can_download_file", False))

    perm.can_change_the_permission = Plus.to_bool(data.get("can_change_the_permission", False))
    perm.can_add_members = Plus.to_bool(data.get("can_add_members", False))
    perm.can_delete_members = Plus.to_bool(data.get("can_delete_members", False))
    perm.can_see_members = Plus.to_bool(data.get("can_see_members", False))

    # 6️⃣ Guardar cambios
    perm.save()

    return {
        "success": True,
        "answer": "",
        "message": "files.title.member-folder-permissions-updated",
        "error": f"Permissions for member {member_id} in folder {folder_id} have been updated."
    }