from django.urls import path
from . import views

urlpatterns = [
    path('rolesAndPermissions/', views.rolesAndPermissions_home, name='rolesAndPermissions_home'),
]
