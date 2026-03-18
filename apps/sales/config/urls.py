from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.sales_home, name='sales_home'),
    path('get_the_sales/', views.get_the_sales, name='get_the_sales'),
    path('add_sale/', views.add_sale, name='add_sale'),
    path('update_sale/', views.update_sale, name='update_sale'),
    path('view_sale/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('get_sale_info/<int:sale_id>/', views.get_sale_info, name='get_sale_info'),
    path('get_sale_history/<int:sale_id>/', views.get_sale_history, name='get_sale_history'),
    path('do_a_sale/<int:sale_id>/', views.do_a_sale, name='do_a_sale'),
    path('cancel_sale/<int:sale_id>/', views.cancel_sale, name='cancel_sale'),
    path('send_buy_email/<int:sale_id>/', views.send_buy_email, name='send_buy_email'),
]
