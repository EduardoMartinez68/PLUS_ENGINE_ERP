import os 
import json

def get_all_the_apps_of_the_erp()->list[str]:
    #get all the apps
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir_folder = os.path.dirname(current_dir)
    parent_dir = os.path.dirname(parent_dir_folder)
    folders = [
        f for f in os.listdir(parent_dir)
        if os.path.isdir(os.path.join(parent_dir, f))
    ]
    return folders

def get_permissions_for_app(app_name: str) -> list[str]:
    #get the permissions of the app of the file permissions.json
    parent_dir_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_dir = os.path.dirname(parent_dir_folder)
    permissions_file_path = os.path.join(parent_dir, app_name, 'permissions.json')

    #here we will see if exist the file in the app and if exist we will read the file
    if os.path.exists(permissions_file_path):
        try:
            with open(permissions_file_path, 'r', encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, IOError):
            pass 

    return []

def get_all_the_permissions() -> dict[str, list[str]]:
    #get all the apps of the erp 
    apps = get_all_the_apps_of_the_erp()
    permissions = {}

    #now we will to read all the permissions that exist in the apps and save all the information in a list
    for app in apps:
        app_permissions = get_permissions_for_app(app)
        permissions[app] = app_permissions
    return permissions
