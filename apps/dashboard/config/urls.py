from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('view_get_information_dashboard/<slug:slug>/', views.view_get_information_dashboard, name='view_get_information_dashboard'),
]
