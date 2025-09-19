from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.services_home, name='services_home'),
]
