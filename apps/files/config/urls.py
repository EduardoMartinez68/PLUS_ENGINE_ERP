from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.files_home, name='files_home'),
]
