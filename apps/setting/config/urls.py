from django.urls import path
from . import views

urlpatterns = [
    path('setting/', views.setting_home, name='setting_home'),
    path('search_branches/', views.search_branches, name='search_branches'),
    path('view_update_company/', views.view_update_company, name='view_update_company'),
    path('view_update_branch/', views.view_update_branch, name='view_update_branch'),
    path('view_update_setting_user/', views.view_update_setting_user, name='view_update_setting_user'),
    path('view_update_data_facture_branch/', views.view_update_data_facture_branch, name='view_update_data_facture_branch'),
    path('view_get_branch_billing_data/', views.view_get_branch_billing_data, name='view_get_branch_billing_data'),
    path('view_update_schedule/', views.view_update_schedule, name='view_update_schedule'),
    path('save_token_whatsapp/', views.save_token_whatsapp, name='save_token_whatsapp'),
    path('whatsapp_callback/', views.whatsapp_callback, name='whatsapp_callback'),
    path('view_update_profile_user/', views.view_update_profile_user, name='view_update_profile_user'),
    path('get_user_notification/<slug:slug>/', views.get_user_notification, name='get_user_notification'),
    path('save_user_notification/<slug:slug>/', views.save_user_notification, name='save_user_notification'),
    path('save_notification_setting/<slug:slug>/', views.save_notification_setting, name='save_notification_setting'),
    path('get_all_notification_settings/', views.get_all_notification_settings, name='get_all_notification_settings'),
]
