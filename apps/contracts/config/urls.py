from django.urls import path
from . import views

urlpatterns = [
    path('contracts', views.contracts_home, name='contracts_home'),
    path('add_contract', views.add_contract, name='add_contract'),
]
