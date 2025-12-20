from django.urls import path
from . import views

urlpatterns = [
    path('profile_online/', views.profile_online_home, name='profile_online_home'),
    path('get_information_of_profile_online/', views.get_information_of_profile_online, name='get_information_of_profile_online'),
    path('view_update_profile_online/', views.view_update_profile_online, name='view_update_profile_online'),
    path('view_add_services/', views.view_add_services, name='view_add_services'),
    path('view_update_services/<int:service_id>/', views.view_update_services, name='view_update_services'),
]
