from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_home, name='sales_home'),
]
