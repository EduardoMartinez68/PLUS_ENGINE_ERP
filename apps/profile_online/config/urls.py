from django.urls import path
from . import views

urlpatterns = [
    path('profile_online/', views.profile_online_home, name='profile_online_home'),
    path('get_information_of_profile_online/', views.get_information_of_profile_online, name='get_information_of_profile_online'),
    path('view_update_profile_online/', views.view_update_profile_online, name='view_update_profile_online'),
    path('view_add_services/', views.view_add_services, name='view_add_services'),
    path('view_update_services/<int:service_id>/', views.view_update_services, name='view_update_services'),
    path('view_update_schedule/', views.view_update_schedule, name='view_update_schedule'),
    path('view_update_address/', views.view_update_address, name='view_update_address'),
    path('view_get_information_about_appoints_online/', views.view_get_information_about_appoints_online, name='view_get_information_about_appoints_online'),
    path('view_add_schedule_online/', views.view_add_schedule_online, name='view_add_schedule_online'),
    path('view_update_schedule_online/<int:id_schedule>/', views.view_update_schedule_online, name='view_update_schedule_online'),
    path('view_profile/<slug:slug>/', views.view_profile, name='view_profile'),
    path('view_schedules_online_json/<slug:slug>/', views.view_schedules_online_json, name='view_schedules_online_json'),
    path('reserve_appointment/<slug:slug>/', views.reserve_appointment, name='reserve_appointment'),
    path('guest_confirm_appointment/<int:appoint_id>/', views.guest_confirm_appointment, name='guest_confirm_appointment'),
]
