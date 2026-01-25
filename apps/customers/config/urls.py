from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customers_home, name='customers_home'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('edit_customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('customers_search/', views.customers_search, name='customers_search'),
    path('get_information_of_the_customer/', views.get_information_of_the_customer, name='get_information_of_the_customer'),
    path('change_status_customer/', views.change_status_customer, name='change_status_customer'),
    path('upload_customer_with_excel/', views.upload_customer_with_excel, name='upload_customer_with_excel'),
    path('download_excel_template/', views.download_excel_template, name='download_excel_template'),
    path('upload_excel_customers/', views.upload_excel_customers, name='upload_excel_customers'),
    path('search_type_customer/', views.search_type_customer, name='search_type_customer'),
    path('search_type_customer_for_id/', views.search_type_customer_for_id, name='search_type_customer_for_id'),
    path('add_type_customer/', views.add_type_customer, name='add_type_customer'),
    path('edit_type_customer/', views.edit_type_customer, name='edit_type_customer'),
    path('delete_type_customer/', views.delete_type_customer, name='delete_type_customer'),
    path('get_customers_with_seeker/', views.get_customers_with_seeker, name='get_customers_with_seeker'),
    path('search_source/', views.search_source, name='search_source'),
    path('search_source_by_id/', views.search_source_by_id, name='search_source_by_id'),
    path('add_source/', views.add_source, name='add_source'),
    path('edit_source/', views.edit_source, name='edit_source'),
    path('delete_source/', views.delete_source, name='delete_source'),
]
