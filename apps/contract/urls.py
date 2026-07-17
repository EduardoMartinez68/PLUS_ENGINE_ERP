from django.urls import path
from . import views

urlpatterns = [
    path('', views.contract_home, name='contract_home'),
]
