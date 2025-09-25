from django.urls import path
from . import views

urlpatterns = [
    path('rolesAndPermissions/', views.rolesAndPermissions_home, name='rolesAndPermissions_home'),
    path('get_all_the_permissions_of_the_erp/', views.get_all_the_permissions_of_the_erp, name='get_all_the_permissions_of_the_erp'),
    path('add_a_new_rol/', views.add_a_new_rol, name='add_a_new_rol'),
]
