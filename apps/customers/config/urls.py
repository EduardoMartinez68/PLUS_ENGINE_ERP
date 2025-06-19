from django.urls import path
from . import views

urlpatterns = [
    path('customers', views.customers_home, name='customers_home'),
]
