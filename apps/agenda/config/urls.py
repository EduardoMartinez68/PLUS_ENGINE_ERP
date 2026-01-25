from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.agenda_home, name='agenda_home'),
    path('create_event/', views.create_event, name='create_event'),
    path('get_events_by_date_range/', views.get_events_by_date_range, name='get_events_by_date_range'),
    path('get_appointment_by_id/', views.get_appointment_by_id, name='get_appointment_by_id'),
    path('search_events/', views.search_events, name='search_events'),
    path('edit_event/', views.edit_event, name='edit_event'),
    path('update_appointment_time_view/', views.update_appointment_time_view, name='update_appointment_time_view'),
    path('delete_event/', views.delete_event, name='delete_event'),
    path('get_the_first_type_events/', views.get_the_first_type_events, name='get_the_first_type_events'),
    path('get_type_event_for_id/', views.get_type_event_for_id, name='get_type_event_for_id'),
    path('create_type_event/', views.create_type_event, name='create_type_event'),
    path('update_type_event/', views.update_type_event, name='update_type_event'),
    path('delete_type_event/', views.delete_type_event, name='delete_type_event'),
    path('setting/', views.setting, name='setting'),
    path('send_reminder_for_email_to_customer/<int:appoint_id>/', views.send_reminder_for_email_to_customer, name='send_reminder_for_email_to_customer'),
    path('google_sync/', views.google_sync, name='google_sync'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
]
