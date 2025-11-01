from django.urls import path
from . import views

urlpatterns = [
    path('', views.odontograma_home, name='odontograma_home'),
]
