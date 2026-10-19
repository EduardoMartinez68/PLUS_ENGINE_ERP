#here we will to create the plugin 
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal
#from apps.agenda.models import Appointment

class DashboardReportSalesPlugin:
    name='DashboardReportSalesPlugin'

    def is_active(self, request):
        return True #this after checking from the database
    
    def is_valid(self,request, data=None):
        #here we will to check all the conditions to return the form
        return True 
    
    def get_name(self):
        return self.name
    
    def save(self, customer, data):
        #code to save address in database
        pass

    def update(self, customer, data):
        #code to update address in database
        pass

    def delete(self, customer):
        #code to delete address from database
        pass

    def search(self, query):
        #code to search address in database
        pass
    







    #------------------------------------------------------------
    def get_sales_by_period(self, user):
        from apps.sales.models import SalePaymentMethod
        from apps.sales.plus_wrapper import Plus

        if not Plus.this_user_have_this_permission(user, 'view_sales_reports'):
            return {"success": False, "message": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'}
        
        branch = user.branch
        now = timezone.now()

        # ===== RANGOS DE FECHA =====
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_week = start_today - timedelta(days=start_today.weekday())
        start_month = start_today.replace(day=1)

        # ===== MES ANTERIOR =====
        # último momento del mes anterior
        end_previous_month = start_month - timedelta(microseconds=1)
        # primer día del mes anterior
        start_previous_month = end_previous_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        periods = {
            "today": (start_today, now),
            "week": (start_week, now),
            "month": (start_month, now),
            "previous_month": (start_previous_month, end_previous_month),
        }

        results = {}

        for period_name, (start_date, end_date) in periods.items():
            payments = SalePaymentMethod.objects.filter(
                branch=branch,
                date__gte=start_date,
                date__lte=end_date
            )

            totals = payments.values('method').annotate(
                total=Sum('amount')
            )

            # Inicializamos métodos en 0
            period_data = {
                'cash': Decimal('0.00'),
                'card': Decimal('0.00'),
                'transfer': Decimal('0.00'),
                'change': Decimal('0.00'),
            }

            for item in totals:
                period_data[item['method']] = item['total'] or Decimal('0.00')

            # Total del periodo (ingresos reales)
            period_data['total'] = (
                period_data['cash'] +
                period_data['card'] +
                period_data['transfer'] +
                period_data['change']
            )

            results[period_name] = period_data

        return results
    
    #this is for get the information of the plugin
    def get_information(self, request, data=None):
        #code to search address in database
        dataInformation = {
            "get_sales_by_period": self.get_sales_by_period(request.user)
        }
        return {"plugin": self.name, "data": dataInformation}

#here we will to save the plugin to the registry
from core.plugins.registry import plugins
plugins.register(
    module="dashboard",
    action="view_information_dashboard", #this is the view where we want to use the plugin
    plugin=DashboardReportSalesPlugin() #this is the plugin instance
)