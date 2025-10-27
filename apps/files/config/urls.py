from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.files_home, name='files_home'),
    path('view_upload_file/', views.view_upload_file, name='view_upload_file'),
    path('view_files_of_the_folder/', views.view_files_of_the_folder, name='view_files_of_the_folder'),
    path('view_folders_of_the_folder/', views.view_folders_of_the_folder, name='view_folders_of_the_folder'),
    path('view_preview_file/<int:file_id>/', views.view_preview_file, name='view_preview_file'),
    path('get_information_file/<int:file_id>/', views.get_information_file, name='get_information_file'),
    path('view_download_file/<int:file_id>/', views.view_download_file, name='view_download_file'),
    path('download_folder_as_zip/<int:folder_id>/', views.download_folder_as_zip, name='download_folder_as_zip'),
    path('view_update_file/<int:file_id>/', views.view_update_file, name='view_update_file'),
    path('view_delete_file/', views.view_delete_file, name='view_delete_file'),
    path('get_information_folder/<int:folder_id>/', views.get_information_folder, name='get_information_folder'),
    path('create_new_folder/', views.create_new_folder, name='create_new_folder'),
    path('edit_folder/<int:folder_id>/', views.edit_folder, name='edit_folder'),
    path('delete_folder_and_his_files/', views.delete_folder_and_his_files, name='delete_folder_and_his_files'),
    path('members_of_folder/', views.members_of_folder, name='members_of_folder'),
    path('view_delete_member_folder/<int:folder_id>/', views.view_delete_member_folder, name='view_delete_member_folder'),
    path('view_add_member_folder/', views.view_add_member_folder, name='view_add_member_folder'),
    path('get_permitions_member/<int:folder_id>/<int:member_id>/', views.get_permitions_member, name='get_permitions_member'),
]
