from django.urls import path
from . import views

urlpatterns = [
    path('', views.rolesAndPermissions_home, name='rolesAndPermissions_home'),
]
