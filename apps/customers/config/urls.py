from django.urls import path
from . import views

urlpatterns = [
    path('search_customers_select/', views.search_customers_select, name='search_customers_select'),
]
