from django.urls import path
from . import views

urlpatterns = [
    path('move_box/', views.move_box_home, name='move_box_home'),
    path('save_move/', views.save_move, name='save_move'),
    path('search_move/', views.search_move, name='search_move'),
]
