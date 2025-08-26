from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.agenda_home, name='agenda_home'),
    path('get_the_first_type_events/', views.get_the_first_type_events, name='get_the_first_type_events'),
    path('create_type_event/', views.create_type_event, name='create_type_event'),
]
