from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employees_home, name='employees_home'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('search_employee/<int:activated>/', views.search_employee, name='search_employee'),
    path('search_branch/', views.search_branch, name='search_branch'),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('view_information_of_the_employee/<int:id>/', views.view_information_of_the_employee, name='view_information_of_the_employee'),
    path('change_status/<int:employee_id>/', views.change_status, name='change_status'),
]
