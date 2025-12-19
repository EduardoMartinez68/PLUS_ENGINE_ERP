from django.urls import path
from . import views

urlpatterns = [
    path('profile_online/', views.profile_online_home, name='profile_online_home'),
    path('get_information_of_profile_online/', views.get_information_of_profile_online, name='get_information_of_profile_online'),
    path('view_update_profile_online/', views.view_update_profile_online, name='view_update_profile_online'),
]
