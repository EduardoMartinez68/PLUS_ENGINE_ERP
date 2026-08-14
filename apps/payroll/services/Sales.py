from core.plus.services import ServiceRegistry
from core.Plus import Plus
from core.plus.decorators import require_permission
from apps.payroll.models import PayrollPeriod
from django.core.paginator import Paginator
from apps.sales.models import Sale
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator

class SalesService:
    @staticmethod
    @require_permission("view_sales")
    @ServiceRegistry.register(
        "payroll.PayrollService.search_sales_for_commissions"
    )
    def search_sales_for_commissions(
        user,
        payroll_period_id,
        employee_id,
        page,
    ):
        """
        Search sales available for commissions.

        Params:
            payroll_period_id : int
            employee_id       : int
            page              : int
        """

        try:
            period = PayrollPeriod.objects.get(
                id=payroll_period_id,
                company=user.company
            )

        except PayrollPeriod.DoesNotExist:
            return {
                "success": False,
                "answer": None,
                "error": "Payroll period was not found."
            }

        filters = Q(
            company=user.company,
            commission_made=False,
            startDate__date__gte=period.start_date,
            startDate__date__lte=period.end_date,
            status__in=["accepted", "paid"],
        )

        if employee_id:
            filters &= Q(user_id=employee_id)

        sales = (
            Sale.objects
            .select_related(
                "branch",
                "customer",
                "user",
            )
            .filter(filters)
            .order_by("-startDate")
        )

        summary = sales.aggregate(
            total_sales=Sum("total"),
            total_paid=Sum("amount_paid"),
            total_pending=Sum("balance"),
        )

        paginator = Paginator(sales, 20)
        page_obj = paginator.get_page(page)

        sales_list = []

        for sale in page_obj:
            sales_list.append({
                "id": sale.id,
                "reference": sale.reference,
                "customer": (
                    'payroll.label.general-public' if sale.customer is None
                    else sale.customer.name
                ),
                "branch": sale.branch.name_branch,
                "start_date": sale.startDate,

                "amount_paid": sale.amount_paid,
                "balance": sale.balance,
                "total": sale.total,
            })

        return {
            "success": True,
            "answer": sales_list,

            "summary": {
                "total_sales": summary["total_sales"] or 0,
                "total_paid": summary["total_paid"] or 0,
                "total_pending": summary["total_pending"] or 0,
                "sales_count": sales.count(),
            },

            "pagination": {
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_records": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },

            "error": "Sales were found successfully."
        }


    @staticmethod
    @require_permission("view_sales")
    @ServiceRegistry.register(
        "payroll.PayrollService.calculate_sales_for_commissions"
    )
    def calculate_sales_for_commissions(
        user,
        payroll_period_id,
        employee_id,
    ):
        """
        Calculate the sales totals available for commissions.

        Params:
            payroll_period_id : int
            employee_id       : int
        """

        try:
            period = PayrollPeriod.objects.get(
                id=payroll_period_id,
                company=user.company
            )

        except PayrollPeriod.DoesNotExist:
            return {
                "success": False,
                "answer": None,
                "error": "Payroll period was not found."
            }

        filters = Q(
            company=user.company,
            commission_made=False,
            startDate__date__gte=period.start_date,
            startDate__date__lte=period.end_date,
            status__in=["accepted", "paid"],
        )

        if employee_id:
            filters &= Q(user_id=employee_id)

        totals = Sale.objects.filter(filters).aggregate(
            sales_count=Count("id"),
            total_sales=Sum("total"),
            total_paid=Sum("amount_paid"),
            total_pending=Sum("balance"),
        )

        return {
            "success": True,
            "answer": {
                "sales_count": totals["sales_count"] or 0,
                "total_sales": totals["total_sales"] or 0,
                "total_paid": totals["total_paid"] or 0,
                "total_pending": totals["total_pending"] or 0,
            },
            "error": "Sales totals calculated successfully."
        }