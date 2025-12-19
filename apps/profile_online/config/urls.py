from django.urls import path
from . import views

urlpatterns = [
    path('profile_online/', views.profile_online_home, name='profile_online_home'),
]
