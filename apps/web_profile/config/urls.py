from django.urls import path
from . import views

urlpatterns = [
    path('web_profile/', views.web_profile_home, name='web_profile_home'),
]
