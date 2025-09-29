from django.urls import path
from . import views

urlpatterns = [
    path('medical_history/', views.medical_history_home, name='medical_history_home'),
    path('get_list_of_medical_history/<int:page>/', views.get_list_of_medical_history, name='get_list_of_medical_history'),
]
