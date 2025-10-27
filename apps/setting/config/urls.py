from django.urls import path
from . import views

urlpatterns = [
    path('setting/', views.setting_home, name='setting_home'),
]
