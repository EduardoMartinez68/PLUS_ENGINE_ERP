import shutil
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings

from .models import Company, Branch
from .models import CustomUser
