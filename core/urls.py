from django.urls import path, include
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
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('singup/', views.register, name='singup'),
    path('whatsapp/webhook/', setting_views.whatsapp_callback, name='whatsapp_webhook'), #this is for whatsapp webhook
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),

    
    #---------------------restart web-------------------
    path('login/reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('login/reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('login/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('login/reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #---------------------web ad----------------
    path('ad/', views.view_ad, name='view_ad'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
for app_path in APPS_FOLDER:
    if isinstance(app_path, str):
        app_name = os.path.basename(app_path)
    else:
        app_name = app_path.name

    #here we will to create a closing for see if exist this module 
    include_path = f'apps.{app_name}.config.urls'
    urlpatterns.append(path(f'{app_name}/', include(include_path)))