#!/usr/bin/env python
import os
import sys
import os
import shutil
import hashlib

import json
from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
#---------------------------------------------------------------CREATE THE DATA OF ENCRYPT FOR SAVE THE INFORMATION------------------------------
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv() #load the variables

#we will see if exist the key in the file .env
key = os.getenv("DATA_ENCRYPTION_KEY")
if not key:
    #if not exist the key, we will to create a data encrypt
    key = Fernet.generate_key().decode()  # decode for save as a string 
    # add the variable to the file .env
    with open(".env", "a") as f:
        f.write(f"\nDATA_ENCRYPTION_KEY={key}\n")
    print("The Key of encrypt  was create with success and save in the file .env")

# create the  cipher
from cryptography.fernet import Fernet
cipher = Fernet(key.encode())

#---------------------------------------------------------------CREATE plus_wrapper IN ALL THE APPS OF THE ERP-----------------------------------
'''
    the file plus_wrapper.py will be created in all apps directories. The file plus_wrapper.py is 
    for that all the apps can use the function of PLUS. 
    The file only remplace other file when exist a change in the file origin 
'''
def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

# Main file we want to copy
source_file = os.path.join(os.path.dirname(__file__), 'plus_wrapper.py')

# Directory that contains all apps
apps_dir = os.path.join(os.path.dirname(__file__), 'apps')

# Check if the source file exists
if not os.path.isfile(source_file):
    print(f"Source file not found: {source_file}")
    exit(1)


source_hash = file_hash(source_file)

# read all the folders 'apps'
for app_name in os.listdir(apps_dir):
    app_path = os.path.join(apps_dir, app_name)
    if os.path.isdir(app_path):
        dest_file = os.path.join(app_path, 'plus_wrapper.py')
        shutil.copy2(source_file, dest_file)  # Copy and overwrite


        #here also we will read the file of permissions if exist for after add the new permissions to the model <Roles_And_Permissions>
        '''
        
        permissions_file = os.path.join(app_path, 'permissions.json')
        if os.path.isfile(permissions_file):
            from core.models import Permits

            try:
                with open(permissions_file, "r", encoding="utf-8") as f:
                    permissions = json.load(f)

                for perm in permissions:
                    Permits.objects.get_or_create(name=perm)
            except (OperationalError, ProgrammingError):
                # Esto evita error si la tabla aún no está creada (ej. antes de migraciones)
                pass
        '''
#---------------------------------------------------------------LOAD ALL THE PLUGINS IN THE ERP FOR CREATE THE NEW VIEWS-----------------------------------
from extensions import load_plugins_and_extensions
load_plugins_and_extensions()


#-----------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    # Set the default Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    try:
        # Import the Django management command executor
        from django.core.management import execute_from_command_line
        # Finally, execute the usual Django management command (e.g., runserver, migrate)
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        # Raise a clear error if Django is not installed
        raise ImportError(
            "Cannot import Django. Are you sure it's installed? "
            "Try running 'pip install django' to install it."
        ) from exc