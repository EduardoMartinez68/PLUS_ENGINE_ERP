from ..models import Folder, FolderPermission, File
from ..plus_wrapper import Plus
from django.db.models import Q

def get_members_of_folder(user, folder_id, search=None):
    """
    Obtiene todos los miembros con permisos en una carpeta específica.
    Si se proporciona 'search', filtra los resultados por nombre o username.
    """
    if not folder_id or str(folder_id).strip() == "":
        return {
            "success": False,
            "message": "files.message.folder-id-invalid",
            "error": "Folder ID is empty or invalid"
        }

    # 1️⃣ Verificar que la carpeta exista
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return {
            "success": False,
            "message": "files.message.folder-not-found",
            "error": f"The folder with id {folder_id} does not exist"
        }

    # 2️⃣ Verificar permisos del usuario actual
    if not Plus.this_user_have_this_permission(user, folder, 'view_members'):
        return {
            "success": False,
            "message": "files.message.no-permission-view-members",
            "error": "User does not have permission to view members of this folder"
        }

    # 3️⃣ Obtener permisos de usuarios con acceso a la carpeta
    permissions = FolderPermission.objects.filter(folder=folder).select_related('user')

    # 4️⃣ Filtrar por búsqueda (si se proporciona)
    if search:
        search = search.strip().lower()
        permissions = permissions.filter(
            Q(user__username__icontains=search) |
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search)
        )

    # 5️⃣ Armar lista de miembros
    members_list = []
    for perm in permissions:
        member = perm.user
        if not member:
            continue  # seguridad extra

        members_list.append({
            "id": member.id,
            "username": member.username,
            "member_name": member.name,
            "email": member.email,
            "avatar": member.avatar.url if member.avatar else None,
            "permissions": {
                "can_read": perm.can_read,
                "can_write": perm.can_write,
                "can_delete": perm.can_delete,
                "can_upload_file": perm.can_upload_file,
                "can_update_file": perm.can_update_file,
                "can_delete_file": perm.can_delete_file,
            }
        })

    return {
        "success": True,
        "answer": members_list,
        "message": "files.message.members-retrieved",
        "error": None
    }