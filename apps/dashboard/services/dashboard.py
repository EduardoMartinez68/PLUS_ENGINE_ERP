from apps.dashboard.services.DashboardService import DashboardService
from core.Plus import Plus

def get_information_dashboard(request, plugin_name=None):
    #here we will to get the information of a plugin that need the dashboard
    answer=DashboardService.get_information_of_a_plugin(request, plugin_name)
    return answer





from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from apps.customers.models import Customer
from apps.sales.models import Sale, SaleItem, SalePaymentMethod, SaleHistory, DataReports
from django.core.cache import cache
from django.db.models import Count, Q, Sum
from dateutil.relativedelta import relativedelta
from apps.payroll.models import Payroll
from decimal import Decimal

def get_today_range():
    now = timezone.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now

def get_week_range():
    now = timezone.now()
    start = now - timedelta(days=now.weekday())  # lunes
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now

def get_month_range():
    now = timezone.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, now

def get_last_month_range():
    now = timezone.now()
    first_day_this_month = now.replace(day=1)
    last_month_end = first_day_this_month - timedelta(seconds=1)
    start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, last_month_end

import hashlib
def get_user_color(user_id):
    hash_int = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)

    palette = [
        "#5B8FF9",  # azul moderno
        "#61DDAA",  # verde menta
        "#65789B",  # azul grisáceo
        "#F6BD16",  # amarillo suave
        "#7262FD",  # índigo elegante
        "#78D3F8",  # azul hielo
        "#9661BC",  # lavanda profesional
        "#F6903D",  # naranja suave
        "#008685",  # turquesa oscuro
        "#F08BB4",  # rosa pastel

        "#7B9ACC",  # azul pastel
        "#8ECFB0",  # verde pastel
        "#B0BEC5",  # gris azulado
        "#A29BFE",  # violeta suave
        "#89CFF0",  # celeste elegante
        "#A8DADC",  # aqua pastel
        "#CDB4DB",  # lila pastel
        "#BDE0FE",  # azul nube
        "#CCD5AE",  # verde salvia
        "#D4A373",  # arena elegante
    ]

    return palette[hash_int % len(palette)]

class Dashboard:

    #this function is for know the money that inside to the clinic
    @classmethod
    def get_income(cls, company, branch, start, end):
        return (
            SalePaymentMethod.objects.filter(
                company=company,
                branch=branch,
                date__range=(start, end)
            )
            .aggregate(total=Sum('amount'))['total'] or 0
        )

    #this function is for know that money outside of the clinic
    @classmethod
    def get_expenses(cls, company, branch, start, end):
        return (
            SalePaymentMethod.objects.filter(
                company=company,
                branch=branch,
                amount__lt=0,  
                date__range=(start, end)
            )
            .aggregate(total=Sum('amount'))['total'] or 0
        )

    @classmethod
    def get_income_today(cls, company, branch):
        start, end = get_today_range()
        income = cls.get_income(company, branch, start, end)
        #expenses = cls.get_expenses(company, branch, start, end)
        return income #+ expenses
    
    @classmethod
    def get_income_week(cls, company, branch):
        start, end = get_week_range()
        income = cls.get_income(company, branch, start, end)
        #expenses = cls.get_expenses(company, branch, start, end)
        return income #- expenses
    
    @classmethod
    def get_all_the_sale_month(cls, company, branch):
        start, end = get_month_range()
        income = cls.get_income(company, branch, start, end)
        expenses = cls.get_expenses(company, branch, start, end)
        return income - expenses
    
    @classmethod
    def get_income_month(cls, company, branch):
        start, end = get_month_range()
        return cls.get_income(company, branch, start, end)

    @classmethod
    def get_cancellations_month(cls, company, branch):
        start, end = get_month_range()
        return cls.get_expenses(company, branch, start, end)

    @classmethod
    def get_profit_last_month(cls, company, branch):
        start, end = get_last_month_range()
        income = cls.get_income(company, branch, start, end)
        #expenses = cls.get_expenses(company, branch, start, end)
        return income #- expenses

    @classmethod
    def get_new_sales_count(cls, company, branch, start, end):
        return Sale.objects.filter(
            company=company,
            branch=branch,
            creationDate__range=(start, end),
            status__in=['pending', 'accepted', 'paid']
        ).count()

    @classmethod
    def get_cancelled_sales_count(cls, company, branch, start, end):
        return Sale.objects.filter(
            company=company,
            branch=branch,
            creationDate__range=(start, end),
            status='cancelled'
        ).count()

    @classmethod
    def get_active_pipeline(cls, company, branch):
        data = Sale.objects.filter(
            company=company,
            branch=branch
        ).aggregate(
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted'))
        )

        return {
            "pending": data["pending"] or 0,
            "accepted": data["accepted"] or 0,
            "total_active": (data["pending"] or 0) + (data["accepted"] or 0)
        }
    
    #----------------------------------UTILITY------------------------
    @classmethod
    def get_utility(cls, company, branch, start, end):
        income = cls.get_income(company, branch, start, end)
        expenses = cls.get_expenses(company, branch, start, end)
        return income - expenses
    
    @classmethod
    def get_utility_complete(cls, company, branch):
        # 🔑 first we will to create the key of the cache
        cache_key = f"utility_complete_{company.id}_{branch.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        start = timezone.make_aware(datetime(2000, 1, 1))
        end = timezone.now()
        income = cls.get_income(company, branch, start, end)
        expenses = cls.get_expenses(company, branch, start, end)
        result=income - expenses
        cache.set(cache_key, result, timeout=60 * 60 * 24 * 30)

        return result

    #----------------------------------CUSTOMERS------------------------
    @classmethod
    def get_data_customers(cls,user, start_month):
        total_customers = Customer.objects.filter(company=user.company).count()

        new_customers = Customer.objects.filter(
            company=user.company,
            creation_date__gte=start_month
        ).count()

        return {
            "total_customers":total_customers,
            "new_customers":new_customers
        }

    #----------------------------------ANALICIS PREDICTIVOS------------------------
    @classmethod
    def get_monthly_income(cls, company, branch, start, end):
        return (
            SaleHistory.objects.filter(
                sale__company=company,
                sale__branch=branch,
                date__range=(start, end)
            ).aggregate(total=Sum('cash_received'))['total'] or 0
        )

    @classmethod
    def predict_next_month_income(cls, company, branch):
        now = timezone.now()

        # 🔑 cache key única por empresa/sucursal
        cache_key = f"prediction_income_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # 📊 obtener últimos 6 meses + actual
        monthly_data = []
        labels = []

        for i in range(6, -1, -1):  # 6 meses atrás hasta hoy
            start = (now - relativedelta(months=i)).replace(day=1, hour=0, minute=0, second=0)
            end = (start + relativedelta(months=1)) - timedelta(seconds=1)

            income = cls.get_monthly_income(company, branch, start, end)

            monthly_data.append(float(income))
            labels.append(start.strftime("%b"))  # Ene, Feb, etc

        # 🧠 REGRESIÓN LINEAL SIMPLE
        n = len(monthly_data)
        x = list(range(n))  # [0,1,2,3,4,5,6]
        y = monthly_data

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(i*j for i, j in zip(x, y))
        sum_x2 = sum(i*i for i in x)

        # fórmula pendiente (m) y b
        denominator = (n * sum_x2 - sum_x**2)
        if denominator == 0:
            prediction = y[-1]  # fallback
        else:
            m = (n * sum_xy - sum_x * sum_y) / denominator
            b = (sum_y - m * sum_x) / n
            prediction = m * n + b  # siguiente punto

        prediction = max(prediction, 0)  # evitar negativos

        # agregar predicción
        monthly_data.append(round(prediction, 2))
        labels.append((now + relativedelta(months=1)).strftime("%b"))

        result = {
            "labels": labels,
            "data": monthly_data
        }

        # 🧊 CACHE (expira en 1 día, suficiente)
        cache.set(cache_key, result, timeout=60 * 60 * 24)

        return result
    
    #------------------------------------ANALITIC OLD-------------------------------
    @classmethod
    def get_top_services(cls, company, branch):
        now = timezone.now()

        cache_key = f"top_services_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 📅 últimos 3 meses
        start = (now - relativedelta(months=3)).replace(day=1, hour=0, minute=0, second=0)

        queryset = (
            SaleItem.objects.filter(
                sale__company=company,
                sale__branch=branch,
                sale__status__in=['accepted', 'paid'],  # ventas reales
                sale__creationDate__gte=start,
                pack__pack_type=1  # solo servicios
            )
            .values('name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:10]  # top 10
        )

        labels = []
        data = []

        for item in queryset:
            labels.append(item['name'])
            data.append(float(item['total_sold']))

        result = {
            "labels": labels,
            "data": data
        }

        # 🧊 cache 1 mes
        cache.set(cache_key, result, timeout=60 * 60 * 24 * 30)

        return result
    
    @classmethod
    def get_top_services_revenue(cls, company, branch):
        now = timezone.now()
        cache_key = f"top_services_revenue_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"

        cached = cache.get(cache_key)
        if cached:
            return cached

        start = (now - relativedelta(months=3)).replace(day=1)

        qs = (
            SaleItem.objects.filter(
                sale__company=company,
                sale__branch=branch,
                sale__status__in=['accepted', 'paid'],
                sale__creationDate__gte=start,
                pack__pack_type=1
            )
            .values('name')
            .annotate(total_money=Sum('total'))
            .order_by('-total_money')[:10]
        )

        result = {
            "labels": [x['name'] for x in qs],
            "data": [float(x['total_money']) for x in qs]
        }

        cache.set(cache_key, result, 60 * 60 * 24 * 30)
        return result
    
    @classmethod
    def get_low_services(cls, company, branch):
        now = timezone.now()
        start = (now - relativedelta(months=3)).replace(day=1)

        qs = (
            SaleItem.objects.filter(
                sale__company=company,
                sale__branch=branch,
                sale__status__in=['accepted', 'paid'],
                sale__creationDate__gte=start,
                pack__pack_type=1
            )
            .values('name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('total_sold')[:5]
        )

        return {
            "labels": [x['name'] for x in qs],
            "data": [float(x['total_sold']) for x in qs]
        }
    
    @classmethod
    def get_data_subscription(cls, user):
        subscription_data = None

        try:
            sub = user.subscription

            subscription_data = {
                "plan": sub.plan.name,
                "status": sub.status,
                "expires_at": sub.current_period_end,
                "is_expired": sub.is_expired()
            }
        except:
            subscription_data = None

        return subscription_data
    
    @classmethod
    def get_top_customers(cls, company, branch):
        now = timezone.now()
        start = (now - relativedelta(months=3)).replace(day=1)

        qs = (
            Sale.objects.filter(
                company=company,
                branch=branch,
                status__in=['accepted', 'paid'],
                creationDate__gte=start
            )
            .values('customer__name')
            .annotate(total=Sum('total'))
            .order_by('-total')[:10]
        )

        return {
            "labels": [x['customer__name'] or "Sin nombre" for x in qs],
            "data": [float(x['total']) for x in qs]
        }

    @classmethod
    def get_payment_methods_distribution(cls, company, branch):
        now = timezone.now()
        start = (now - relativedelta(months=3)).replace(day=1)

        qs = (
            SalePaymentMethod.objects.filter(
                company=company,
                branch=branch,
                date__gte=start
            )
            .values('method')
            .annotate(total=Sum('amount'))
        )

        return {
            "labels": [x['method'] for x in qs],
            "data": [float(x['total']) for x in qs]
        }
    
    @classmethod
    def get_top_doctors_by_revenue(cls, company, branch):
        now = timezone.now()

        cache_key = f"top_doctors_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 📅 últimos 3 meses
        start = (now - relativedelta(months=3)).replace(day=1, hour=0, minute=0, second=0)

        queryset = (
            Sale.objects.filter(
                company=company,
                branch=branch,
                status__in=['accepted', 'paid'],
                creationDate__gte=start,
                user__isnull=False
            )
            .values('user__id', 'user__name')  # puedes cambiar a nombre real
            .annotate(total_revenue=Sum('total'))
            .order_by('-total_revenue')[:10]
        )

        labels = []
        data = []
        colors=[]
        background_colors=[]

        for item in queryset:
            name = item['user__name'] or f"User {item['user__id']}"
            user_id = item['user__id']
            labels.append(name)
            data.append(float(item['total_revenue']))

            color_user=get_user_color(user_id)
            colors.append(color_user)
            background_colors.append(color_user)

        result = {
            "labels": labels,
            "data": data,
            "backgroundColor":colors,
            "borderColor":background_colors
        }

        # 🧊 cache 1 mes
        cache.set(cache_key, result, timeout=60 * 60 * 24 * 30)

        return result
    

    @classmethod
    def get_doctors_income_current_month(cls, company, branch):
        now = timezone.now()

        # 📅 inicio del mes
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 🔑 cache mensual
        cache_key = f"doctors_income_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        queryset = (
            Sale.objects.filter(
                company=company,
                branch=branch,
                status__in=['accepted', 'paid'],
                creationDate__gte=start,
                user__isnull=False
            )
            .values('user__id', 'user__username')
            .annotate(total_income=Sum('total'))
            .order_by('-total_income')
        )

        labels = []
        data = []

        for item in queryset:
            name = item['user__username'] or f"User {item['user__id']}"
            labels.append(name)
            data.append(float(item['total_income']))

        result = {
            "labels": labels,
            "data": data
        }

        # 🧊 cache (1 día, porque este dato cambia constantemente)
        cache.set(cache_key, result, timeout=60 * 60 * 24)

        return result
    
    @classmethod
    def get_customers_by_source(cls, company, branch):
        now = timezone.now()

        # 🔑 cache mensual
        cache_key = f"customers_source_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        queryset = (
            Customer.objects.filter(
                company=company,
                branch=branch,
                activated=True
            )
            .values('source__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        labels = []
        data = []

        for item in queryset:
            source_name = item['source__name'] or "Sin fuente"
            labels.append(source_name)
            data.append(item['total'])

        result = {
            "labels": labels,
            "data": data
        }

        # 🧊 cache 30 días (mensual)
        cache.set(cache_key, result, timeout=60 * 60 * 24 * 30)

        return result
    
    @classmethod
    def get_revenue_by_source(cls, company, branch):
        now = timezone.now()

        cache_key = f"revenue_source_{company.id}_{branch.id}_{now.strftime('%Y-%m')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        qs = (
            Sale.objects.filter(
                company=company,
                branch=branch,
                status__in=['accepted', 'paid']
            )
            .values('customer__source__name')
            .annotate(total=Sum('total'))
            .order_by('-total')
        )

        result = {
            "labels": [x['customer__source__name'] or "Sin fuente" for x in qs],
            "data": [float(x['total']) for x in qs]
        }
    

    #-------------------------------------------------------distributions-------------------------
    @classmethod
    def get_area_color(cls, area_id):
        AREA_COLORS = [
            "#3B82F6",  # blue
            "#10B981",  # emerald
            "#F59E0B",  # amber
            "#EF4444",  # red
            "#8B5CF6",  # violet
            "#06B6D4",  # cyan
            "#EC4899",  # pink
            "#84CC16",  # lime
            "#F97316",  # orange
            "#14B8A6",  # teal
            "#6366F1",  # indigo
            "#A855F7",  # purple
        ]
        index = area_id % len(AREA_COLORS)
        return AREA_COLORS[index]


 
    @classmethod
    def get_financial_summary(cls, company, branch):
        current_year = timezone.now().year #get the year currency
        cache_key =  f"financial_summary_{company.id}_{branch.id}_{current_year}"

        cached = cache.get(cache_key)
        if cached:
            return cached


        totals = (
            DataReports.objects
            .filter(
                company=company,
                branch=branch,
                year=current_year
            )
            .aggregate(
                total_inside=Sum("total_inside_money"),
                total_outside=Sum("total_outside_money")
            )
        )

        total_inside = float(totals["total_inside"] or 0)
        total_outside = float(totals["total_outside"] or 0)

        result = {
            "total_inside_money": total_inside,
            "total_outside_money": total_outside,
            "total_profit": total_inside - total_outside
        }

        cache.set(cache_key, result, timeout=60 * 10) #10 minutes cache

        return result


    # ---------------------------------- PAYROLL ----------------------------------
    @classmethod
    def get_data_payroll(cls, user):
        """
        Return payroll expenses for dashboard.
        """

        today = timezone.localdate()

        # ---------------- Current week ----------------
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)

        # ---------------- Previous week ----------------
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start

        # ---------------- Current month ----------------
        month_start = today.replace(day=1)

        # ---------------- Previous month ----------------
        if month_start.month == 1:
            last_month_start = month_start.replace(
                year=month_start.year - 1,
                month=12
            )
        else:
            last_month_start = month_start.replace(
                month=month_start.month - 1
            )

        last_month_end = month_start

        current_week = (
            Payroll.objects.filter(
                company=user.company,
                payment_date__date__gte=week_start,
                payment_date__date__lt=week_end,
            ).aggregate(
                total=Sum("total")
            )["total"]
            or Decimal("0.00")
        )

        previous_week = (
            Payroll.objects.filter(
                company=user.company,
                payment_date__date__gte=last_week_start,
                payment_date__date__lt=last_week_end,
            ).aggregate(
                total=Sum("total")
            )["total"]
            or Decimal("0.00")
        )

        current_month = (
            Payroll.objects.filter(
                company=user.company,
                payment_date__date__gte=month_start,
                payment_date__date__lte=today,
            ).aggregate(
                total=Sum("total")
            )["total"]
            or Decimal("0.00")
        )

        previous_month = (
            Payroll.objects.filter(
                company=user.company,
                payment_date__date__gte=last_month_start,
                payment_date__date__lt=last_month_end,
            ).aggregate(
                total=Sum("total")
            )["total"]
            or Decimal("0.00")
        )

        return {
            "current_week": current_week,
            "previous_week": previous_week,
            "current_month": current_month,
            "previous_month": previous_month,
        }

    #-------------------------------------------------------get all the information of the dashbord-------------------------
    @classmethod
    def get_dashboard_data(cls, user):
        #try get the cache of the dashboard
        cache_key = f"dashboard_data_user_{user.id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        now = timezone.now()
        start_month = now.replace(day=1, hour=0, minute=0, second=0)
        last_month = (start_month - timedelta(days=1)).replace(day=1)
        
        try:
            company=user.company
            branch=user.branch

            today_start, today_end = get_today_range()
            month_start, month_end = get_month_range()


        
            # =========================
            # RESPONSE
            # =========================
            response= {
                "success": True,
                "message": "",
                "error": "",
                "answer": {
                    "KPI":{
                        "income_today": cls.get_income_today(company, branch),
                        "income_week": cls.get_income_week(company, branch),
                        "get_all_the_sale_month":cls.get_all_the_sale_month(company,branch), #pendiente
                        "income_month": cls.get_income_month(company, branch),
                        "cancellations_month": cls.get_cancellations_month(company, branch),
                        "profit_last_month": cls.get_profit_last_month(company, branch),

                        "new_sales": cls.get_new_sales_count(company, branch, today_start, today_end),
                        "cancelled_sales": cls.get_cancelled_sales_count(company, branch, today_start, today_end),
                        "get_active_pipeline": cls.get_active_pipeline(company, branch),
                        "utility_current_month": cls.get_utility(company, branch, month_start, month_end),
                        "utility_complete": cls.get_utility_complete(company, branch),
                        "payroll": cls.get_data_payroll(user)
                    },
                    "customers": cls.get_data_customers(user, start_month),
                    "graph":{
                        "get_top_services":cls.get_top_services(company, branch),
                        "get_top_services_revenue":cls.get_top_services_revenue(company, branch),
                        "get_low_services":cls.get_low_services(company, branch),
                        "get_top_customers":cls.get_top_customers(company, branch),
                        "get_payment_methods_distribution":cls.get_payment_methods_distribution(company, branch),
                        "get_top_doctors_by_revenue":cls.get_top_doctors_by_revenue(company, branch),
                        "get_doctors_income_current_month":cls.get_doctors_income_current_month(company, branch),
                        "get_customers_by_source":cls.get_customers_by_source(company,branch),
                        "get_revenue_by_source":cls.get_revenue_by_source(company, branch),
                    },
                    "graph_prediction": {
                        "predict_next_month_income": cls.predict_next_month_income(company, branch)
                    },
                    "subscription": cls.get_data_subscription(user),
                    "financial_summary": cls.get_financial_summary(company, branch)
                }
            }

            cache.set(cache_key, response, timeout=60) #save the cache
            return response


        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": str(e),
                "answer": {}
            }