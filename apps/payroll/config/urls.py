from django.urls import path
from . import views

urlpatterns = [
    path('payroll/', views.payroll_home, name='payroll_home'),
    path('view_employees_contracts/', views.view_employees_contracts, name='view_employees_contracts'),
    path('view_search_employees_contracts/', views.view_search_employees_contracts, name='view_search_employees_contracts'),
    path('create_employee_contract/', views.create_employee_contract, name='create_employee_contract'),
    path('update_employee_contract/<int:contract_id>/', views.update_employee_contract, name='update_employee_contract'),
    path('get_employee_contract/<int:contract_id>/', views.get_employee_contract, name='get_employee_contract'),
]
