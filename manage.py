#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Set the default Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    try:
        # Import the Django management command executor
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Raise a clear error if Django is not installed
        raise ImportError(
            "Cannot import Django. Are you sure it's installed? "
            "Try running 'pip install django' to install it."
        ) from exc

    # First, try to run the function that generates all models from the database
    # Assumes you have a script named 'generate_all_models.py' in the project root
    # with a function called 'generate_all_models()'
    
    try:
        from generate_all_models import create_models
        create_models()
    except ImportError:
        print("Module 'generate_all_models.py' not found or not in PYTHONPATH.")
    except AttributeError:
        print("The module 'generate_all_models.py' does not have a function 'generate_all_models()'.")

    # Finally, execute the usual Django management command (e.g., runserver, migrate)
    execute_from_command_line(sys.argv)
