from django.urls import path
from . import views

urlpatterns = [
    path('setting/', views.setting_home, name='setting_home'),
    path('view_update_company/', views.view_update_company, name='view_update_company'),
    path('view_update_branch/', views.view_update_branch, name='view_update_branch'),
]
