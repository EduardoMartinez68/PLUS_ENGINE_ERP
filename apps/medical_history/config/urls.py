from django.urls import path
from . import views

urlpatterns = [
    path('medical_history/', views.medical_history_home, name='medical_history_home'),
    path('get_list_of_medical_history/<int:page>/', views.get_list_of_medical_history, name='get_list_of_medical_history'),
    path('view_history_medical/<int:customer_id>/', views.view_history_medical, name='view_history_medical'),
    path('get_medical_history_with_customer_id/<int:customer_id>/', views.get_medical_history_with_customer_id, name='get_medical_history_with_customer_id'),
    path('get_form_medical_history/<int:customer_id>/', views.get_form_medical_history, name='get_form_medical_history'),
    path('form_history_medical/<int:customer_id>/', views.form_history_medical, name='form_history_medical'),
]
