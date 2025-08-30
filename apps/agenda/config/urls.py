from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.agenda_home, name='agenda_home'),
    path('create_event/', views.create_event, name='create_event'),
    path('get_events_by_date_range/', views.get_events_by_date_range, name='get_events_by_date_range'),
    path('edit_event/', views.edit_event, name='edit_event'),
    path('get_the_first_type_events/', views.get_the_first_type_events, name='get_the_first_type_events'),
    path('create_type_event/', views.create_type_event, name='create_type_event'),
]
