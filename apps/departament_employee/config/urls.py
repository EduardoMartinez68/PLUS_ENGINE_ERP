from django.urls import path
from . import views

urlpatterns = [
    path('departament_employee/', views.departament_employee_home, name='departament_employee_home'),
    path('search_employee_department/<int:activated>/', views.search_employee_department, name='search_employee_department'),
    path('get_information_of_the_departament/<int:departament_id>/', views.get_information_of_the_departament, name='get_information_of_the_departament'),
    path('add_new_departament/', views.add_new_departament, name='add_new_departament'),
    path('edit_departament/', views.edit_departament, name='edit_departament'),
    path('delete_departament/', views.delete_departament, name='delete_departament'),
    path('search_employee/', views.search_employee, name='search_employee'),
]
