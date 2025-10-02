from django.urls import path
from . import views

urlpatterns = [
    path('', views.departament_employee_home, name='departament_employee_home'),
]
