from django.urls import path
from . import views

urlpatterns = [
    path('', views.cases_home, name='cases_home'),
]
