from django.urls import path
from . import views

urlpatterns = [
    path('departament_employee/', views.departament_employee_home, name='departament_employee_home'),
    path('search_employee_department/<int:activated>/', views.search_employee_department, name='search_employee_department'),
]
