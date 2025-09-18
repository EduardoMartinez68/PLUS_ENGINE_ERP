from django.urls import path
from . import views

urlpatterns = [
    path('', views.medical_history_home, name='medical_history_home'),
]
