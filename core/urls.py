from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from . import views
from core.readApps import APPS_FOLDER
import os

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('singup/', views.register, name='singup'),
]

for app_path in APPS_FOLDER:
    if isinstance(app_path, str):
        app_name = os.path.basename(app_path)
    else:
        app_name = app_path.name

    include_path = f'apps.{app_name}.config.urls'

    urlpatterns.append(path(f'{app_name}/', include(include_path)))

