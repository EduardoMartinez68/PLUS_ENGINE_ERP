#!/usr/bin/env python
import os
import sys
import os
import shutil
import hashlib
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