'''
this both functions are for calculate the space that the user have in the server and if can upload more 
files to his count. If the user is use the software in desktop, the can upload all the files that need unlimited.
'''
from django.db.models import Sum
from ..models import Folder, FolderPermission, File

def user_storage_used(user):
    return File.objects.filter(upload_user=user).aggregate(total=Sum('size'))['total'] or 0

def can_upload(user, filesize):
    limit = get_limit_of_the_user() * 1024 * 1024 * 1024  # 1 GiB
    return user_storage_used(user) + filesize <= limit

def get_limit_of_the_user():
    #here we will see the pack that have the user in the subscription and return the size of his space
    #pack 1==1 GiB
    #pack 2==5 GiB
    return 1

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