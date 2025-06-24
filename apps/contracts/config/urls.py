from django.urls import path
from . import views

urlpatterns = [
    path('contracts/', views.contracts_home, name='contracts_home'),
    path('add_contract/', views.add_contract, name='add_contract'),
    path('edit_contract/<int:contract_id>/', views.edit_contract, name='edit_contract'),
    path('download_contract/<int:contract_id>/', views.download_contract, name='download_contract'),
]
