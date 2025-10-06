from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employees_home, name='employees_home'),
]
