from django.urls import path
from . import views

urlpatterns = [
    path('cases/', views.cases_home, name='cases_home'),
    path('left_out/', views.left_out, name='left_out'),
    path('case_2/', views.case_home_2, name='case_home_2'),
]
