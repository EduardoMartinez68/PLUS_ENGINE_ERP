from django.urls import path
from . import views

urlpatterns = [
    path('medical_history/', views.medical_history_home, name='medical_history_home'),
    path('get_list_of_medical_history/<int:page>/', views.get_list_of_medical_history, name='get_list_of_medical_history'),
    path('medical_history/<int:customer_id>/', views.medical_history, name='medical_history'),
    path('get_medical_history_with_customer_id/<int:customer_id>/', views.get_medical_history_with_customer_id, name='get_medical_history_with_customer_id'),
]
