from django.urls import path
from . import views

urlpatterns = [
    path('payroll/', views.payroll_home, name='payroll_home'),
]
