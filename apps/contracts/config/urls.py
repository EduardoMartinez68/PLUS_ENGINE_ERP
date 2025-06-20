from django.urls import path
from . import views

urlpatterns = [
    path('contracts', views.contracts_home, name='contracts_home'),
]
