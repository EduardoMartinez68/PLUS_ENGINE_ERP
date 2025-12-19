from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView


from . import views
from apps.setting.links import views as setting_views
from core.readApps import APPS_FOLDER
import os

#here is for load all the image that of the apps like customers, products, etc.
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('singup/', views.register, name='singup'),
    path('whatsapp/webhook/', setting_views.whatsapp_callback, name='whatsapp_webhook'), #this is for whatsapp webhook
    path("profile/<slug:slug>/",views.view_profile, name="view_profile"), #this is for the profile of the professionals 
]


for app_path in APPS_FOLDER:
    if isinstance(app_path, str):
        app_name = os.path.basename(app_path)
    else:
        app_name = app_path.name

    include_path = f'apps.{app_name}.config.urls'

    urlpatterns.append(path(f'{app_name}/', include(include_path)))
    




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



