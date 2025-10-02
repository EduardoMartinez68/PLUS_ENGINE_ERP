from django.urls import path
from . import views

urlpatterns = [
    path('departament_employee/', views.departament_employee_home, name='departament_employee_home'),
]
