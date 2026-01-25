import os
import django
from django.core import management

def create_models():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Ajusta según tu proyecto
    django.setup()

    with open('database/models.py', 'w', encoding='utf-8') as f:
        management.call_command('inspectdb', database='default', stdout=f)

#create_models()
