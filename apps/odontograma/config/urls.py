from django.urls import path
from . import views

urlpatterns = [
    path('odontograma/', views.odontograma_home, name='odontograma_home'),
    path('search_odontogram/', views.search_odontogram, name='search_odontogram'),
    path('add_odontogram/', views.add_odontogram, name='add_odontogram'),
    path('view_odontogram/<int:odontogram_id>/', views.view_odontogram, name='view_odontogram'),
    path('get_odontogram/<int:odontogram_id>/', views.get_odontogram, name='get_odontogram'),
    path('get_information_of_the_odotngoram/<int:odontogram_id>/', views.get_information_of_the_odotngoram, name='get_information_of_the_odotngoram'),
]
