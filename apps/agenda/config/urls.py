from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.agenda_home, name='agenda_home'),
    path('create_type_event/', views.create_type_event, name='create_type_event'),
]
