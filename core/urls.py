from django.urls import path, include
from . import views
from core.readApps import APPS_FOLDER
import os

urlpatterns = [
    path('', views.home, name='home'),
]

for app_path in APPS_FOLDER:
    if isinstance(app_path, str):
        app_name = os.path.basename(app_path)
    else:
        app_name = app_path.name

    include_path = f'apps.{app_name}.config.urls'

    urlpatterns.append(path(f'{app_name}/', include(include_path)))

