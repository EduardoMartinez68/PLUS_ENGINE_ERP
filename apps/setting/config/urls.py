from django.urls import path
from . import views

urlpatterns = [
    path('setting/', views.setting_home, name='setting_home'),
    path('view_update_company/', views.view_update_company, name='view_update_company'),
    path('view_update_branch/', views.view_update_branch, name='view_update_branch'),
    path('view_update_setting_user/', views.view_update_setting_user, name='view_update_setting_user'),
    path('view_update_data_facture_branch/', views.view_update_data_facture_branch, name='view_update_data_facture_branch'),
    path('view_get_branch_billing_data/', views.view_get_branch_billing_data, name='view_get_branch_billing_data'),
    path('view_update_schedule/', views.view_update_schedule, name='view_update_schedule'),
    path('whatsapp_callback/', views.whatsapp_callback, name='whatsapp_callback'),
    path('view_update_profile_user/', views.view_update_profile_user, name='view_update_profile_user'),
]
