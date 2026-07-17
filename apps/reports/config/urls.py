from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.reports_home, name='reports_home'),
    path('search_reports_move/', views.search_reports_move, name='search_reports_move'),
    path('search_reports_sales/', views.search_reports_sales, name='search_reports_sales'),
    path('download_excel_sale/', views.download_excel_sale, name='download_excel_sale'),
    path('download_pdf_sale/', views.download_pdf_sale, name='download_pdf_sale'),
    path('download_excel_payment_methods/', views.download_excel_payment_methods, name='download_excel_payment_methods'),
    path('download_pdf_payment_methods/', views.download_pdf_payment_methods, name='download_pdf_payment_methods'),
    path('get_report_inventory/', views.get_report_inventory, name='get_report_inventory'),
    path('get_report_history_inventory/', views.get_report_history_inventory, name='get_report_history_inventory'),
    path('download_pdf_inventory/', views.download_pdf_inventory, name='download_pdf_inventory'),
]
