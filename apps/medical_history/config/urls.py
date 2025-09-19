from django.urls import path
from . import views

urlpatterns = [
    path('medical_history/', views.medical_history_home, name='medical_history_home'),
]
