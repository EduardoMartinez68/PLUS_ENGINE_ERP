from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.services_home, name='services_home'),
    path('search_pack/<int:activate>/', views.search_pack, name='search_pack'),
    path('add_services/', views.add_services, name='add_services'),
    path('update_services/', views.update_services, name='update_services'),
    path('delete_services/<int:services_id>/', views.delete_services, name='delete_services'),
    path('restart_services/<int:services_id>/', views.restart_services, name='restart_services'),
    path('get_information_product/<int:product_id>/', views.get_information_product, name='get_information_product'),
    path('search_tax/', views.search_tax, name='search_tax'),
    path('add_tax/', views.add_tax, name='add_tax'),
    path('get_information_tax/<int:tax_id>/', views.get_information_tax, name='get_information_tax'),
    path('update_tax/<int:tax_id>/', views.update_tax, name='update_tax'),
    path('search_departament/', views.search_departament, name='search_departament'),
    path('add_departament/', views.add_departament, name='add_departament'),
    path('update_departament/<int:departament_id>/', views.update_departament, name='update_departament'),
    path('delete_departament/', views.delete_departament, name='delete_departament'),
    path('get_information_departament/<int:departament_id>/', views.get_information_departament, name='get_information_departament'),
    path('search_category/', views.search_category, name='search_category'),
    path('add_category/', views.add_category, name='add_category'),
    path('update_category/<int:category_id>/', views.update_category, name='update_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('get_information_category/<int:category_id>/', views.get_information_category, name='get_information_category'),
]
