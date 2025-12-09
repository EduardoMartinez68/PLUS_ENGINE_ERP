from django.urls import path
from . import views

urlpatterns = [
    path('odontograma/', views.odontograma_home, name='odontograma_home'),
    path('search_odontogram/', views.search_odontogram, name='search_odontogram'),
    path('add_odontogram/', views.add_odontogram, name='add_odontogram'),
    path('view_odontogram/<int:odontogram_id>/', views.view_odontogram, name='view_odontogram'),
    path('get_information_of_the_odotngoram/<int:odontogram_id>/', views.get_information_of_the_odotngoram, name='get_information_of_the_odotngoram'),
    path('view_update_tooth/<int:odontogram_id>/<int:tooth_id>/', views.view_update_tooth, name='view_update_tooth'),
    path('update_periodontogram/<int:periodontogram_id>/', views.update_periodontogram, name='update_periodontogram'),
    path('view_setting/', views.view_setting, name='view_setting'),
    path('get_information_of_the_history_odotngoram/<int:odontogram_id>/', views.get_information_of_the_history_odotngoram, name='get_information_of_the_history_odotngoram'),
    path('create_odontogram_history/<int:odontogram_id>/', views.create_odontogram_history, name='create_odontogram_history'),
    path('change_father_odontogram/<int:odontogram_id>/', views.change_father_odontogram, name='change_father_odontogram'),
]
