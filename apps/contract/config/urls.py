from django.urls import path
from . import views

urlpatterns = [
    path('contract/', views.contract_home, name='contract_home'),
    path('view_search_contract_templates/', views.view_search_contract_templates, name='view_search_contract_templates'),
    path('view_create_contract_template/', views.view_create_contract_template, name='view_create_contract_template'),
    path('view_update_contract_template/<int:template_id>/', views.view_update_contract_template, name='view_update_contract_template'),
    path('view_delete_contract_template/<int:template_id>/', views.view_delete_contract_template, name='view_delete_contract_template'),
    path('view_get_contract_template/<int:template_id>/', views.view_get_contract_template, name='view_get_contract_template'),
]
