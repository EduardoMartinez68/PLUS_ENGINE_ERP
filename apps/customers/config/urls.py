from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customers_home, name='customers_home'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('edit_customer/<int:id_customer>/', views.edit_customer, name='edit_customer'),
    path('customers_search/', views.customers_search, name='customers_search'),
    path('get_information_of_the_customer/', views.get_information_of_the_customer, name='get_information_of_the_customer'),
    path('search_type_customer/', views.search_type_customer, name='search_type_customer'),
    path('search_type_customer_for_id/', views.search_type_customer_for_id, name='search_type_customer_for_id'),
    path('add_type_customer/', views.add_type_customer, name='add_type_customer'),
    path('edit_customer/', views.edit_customer, name='edit_customer'),
    path('search_customers_select/', views.search_customers_select, name='search_customers_select'),
]
