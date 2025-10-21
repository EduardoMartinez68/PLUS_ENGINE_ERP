from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.files_home, name='files_home'),
    path('upload_file/<int:folder_id>/', views.upload_file, name='upload_file'),
    path('view_files_of_the_folder/', views.view_files_of_the_folder, name='view_files_of_the_folder'),
    path('view_folders_of_the_folder/', views.view_folders_of_the_folder, name='view_folders_of_the_folder'),
    path('get_information_folder/<int:folder_id>/', views.get_information_folder, name='get_information_folder'),
    path('create_new_folder/', views.create_new_folder, name='create_new_folder'),
    path('edit_folder/<int:folder_id>/', views.edit_folder, name='edit_folder'),
    path('delete_folder_and_his_files/', views.delete_folder_and_his_files, name='delete_folder_and_his_files'),
]
