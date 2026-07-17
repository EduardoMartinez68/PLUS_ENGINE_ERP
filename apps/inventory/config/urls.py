from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_home, name='inventory_home'),
    path('get_data_inventory/<int:pack_id>/', views.get_data_inventory, name='get_data_inventory'),
    path('get_inventory/', views.get_inventory, name='get_inventory'),
    path('update_inventory/', views.update_inventory, name='update_inventory'),
    path('get_history_inventory/', views.get_history_inventory, name='get_history_inventory'),
]
