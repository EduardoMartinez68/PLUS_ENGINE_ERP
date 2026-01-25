from django.urls import path
from . import views

urlpatterns = [
    path('', views.setting_home, name='setting_home'),
]
