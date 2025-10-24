#-----------------------permissions-----------------------
from ..models import Folder, FolderPermission, File
from ..plus_wrapper import Plus

def has_folder_permission(user, folder, action: str) -> bool:
    """
    Verifica si el usuario tiene permiso sobre una carpeta para realizar una acción específica.
    Si el usuario es el creador de la carpeta, tiene todos los permisos automáticamente.
    
    :param user: CustomUser
    :param folder: Folder o ID de la carpeta
    :param action: cadena como 'edit_folder', 'delete_file', 'add_members', etc.
    :return: bool
    """
    if not user or not folder:
        return False

    # 📁 Si se pasa un ID en lugar del objeto Folder
    if isinstance(folder, int):
        try:
            folder = Folder.objects.get(id=folder)
        except Folder.DoesNotExist:
            return False

    # 👑 Si el usuario es el creador de la carpeta → acceso total
    if folder.creator_user_id == user.id:
        return True

    # 🔎 Buscar permisos específicos del usuario en la carpeta
    try:
        permission = FolderPermission.objects.get(folder=folder, user=user)
    except FolderPermission.DoesNotExist:
        return False

    # 🔹 Mapeo de acciones a campos del modelo
    action_map = {
        # --- Permisos sobre la carpeta ---
        "edit_folder": permission.can_edit_folder,
        "delete_folder": permission.can_delete_folder,
        "download_folder": permission.can_download_folder,
        "add_subfolder": permission.can_add_subfolder,

        # --- Permisos sobre archivos ---
        "see_files": permission.can_see_the_files,
        "upload_file": permission.can_upload_file,
        "move_file": permission.can_move_file,
        "update_file": permission.can_update_file,
        "copy_file": permission.can_copy_file,
        "delete_file": permission.can_delete_file,
        "see_file": permission.can_see_file,
        "download_file": permission.can_download_file,

        # --- Permisos de gestión ---
        "change_permission": permission.can_change_the_permission,
        "add_members": permission.can_add_members,
        "delete_members": permission.can_delete_members,
    }

    # ✅ Retornar el permiso correspondiente (o False si no existe)
    return action_map.get(action, False)
