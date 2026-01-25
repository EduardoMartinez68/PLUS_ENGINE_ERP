from django.urls import path
from . import views

urlpatterns = [
    path('rolesAndPermissions/', views.rolesAndPermissions_home, name='rolesAndPermissions_home'),
    path('get_information_of_the_role/<int:activated>/', views.get_information_of_the_role, name='get_information_of_the_role'),
    path('get_all_the_permissions_of_the_erp/', views.get_all_the_permissions_of_the_erp, name='get_all_the_permissions_of_the_erp'),
    path('add_a_new_rol/', views.add_a_new_rol, name='add_a_new_rol'),
    path('edit_rol/<int:rol_id>/', views.edit_rol, name='edit_rol'),
    path('duplicate_rol_in_the_company/<int:rol_id>/', views.duplicate_rol_in_the_company, name='duplicate_rol_in_the_company'),
    path('get_information_rol/<int:rol_id>/', views.get_information_rol, name='get_information_rol'),
    path('change_status/', views.change_status, name='change_status'),
]
