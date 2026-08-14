from django.urls import path
from . import views

urlpatterns = [
    path('payroll/', views.payroll_home, name='payroll_home'),
    path('view_employees_contracts/', views.view_employees_contracts, name='view_employees_contracts'),
    path('view_search_employees_contracts/', views.view_search_employees_contracts, name='view_search_employees_contracts'),
    path('create_employee_contract/', views.create_employee_contract, name='create_employee_contract'),
    path('update_employee_contract/<int:contract_id>/', views.update_employee_contract, name='update_employee_contract'),
    path('get_employee_contract/<int:contract_id>/', views.get_employee_contract, name='get_employee_contract'),
    path('search_payrollperiod/', views.search_payrollperiod, name='search_payrollperiod'),
    path('create_payrollperiod/', views.create_payrollperiod, name='create_payrollperiod'),
    path('view_payrollperiod/<int:payrollperiod_id>/', views.view_payrollperiod, name='view_payrollperiod'),
    path('search_payroll/', views.search_payroll, name='search_payroll'),
    path('get_payroll_by_id/<int:payroll_id>/', views.get_payroll_by_id, name='get_payroll_by_id'),
    path('buy_payroll/<int:payroll_id>/', views.buy_payroll, name='buy_payroll'),
    path('create_payroll/', views.create_payroll, name='create_payroll'),
    path('search_sale/<int:payroll_period_id>/', views.search_sale, name='search_sale'),
    path('get_total_sale/<int:payroll_period_id>/', views.get_total_sale, name='get_total_sale'),
    path('update_commissions/<int:payroll_id>/', views.update_commissions, name='update_commissions'),
]
