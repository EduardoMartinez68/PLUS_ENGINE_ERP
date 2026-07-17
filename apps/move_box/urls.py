from django.urls import path
from . import views

urlpatterns = [
    path('', views.move_box_home, name='move_box_home'),
]
