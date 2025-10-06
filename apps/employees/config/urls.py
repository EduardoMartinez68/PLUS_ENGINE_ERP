from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employees_home, name='employees_home'),
    path('search_employee/<int:activated>/', views.search_employee, name='search_employee'),
    path('search_branch/', views.search_branch, name='search_branch'),
]
