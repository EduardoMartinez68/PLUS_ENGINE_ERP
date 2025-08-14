from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customers_home, name='customers_home'),
    path('edit_customer/<int:id_customer>/', views.edit_customer, name='edit_customer'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('search_customers/', views.search_customers, name='search_customers'),
    path('search_customers_select/', views.search_customers_select, name='search_customers_select'),
]
