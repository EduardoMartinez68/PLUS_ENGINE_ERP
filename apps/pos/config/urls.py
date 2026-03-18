from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_home, name='pos_home'),
]
