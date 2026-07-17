from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from ..plus_wrapper import Plus
from apps.sales.models import Sale
from decimal import Decimal
import threading
from django.db.models import F
from django.conf import settings 
from django.db.models import Sum

class ReportsSales:
    @classmethod
    def search(
        cls,
        user,
        key=None,
        page=1,
        view_sales_totals=False,
        customer_id=None,
        user_id=None,
        branch_id=None,
        date_start=None,
        date_end=None,
        status=None
    ):

        try:

            query = Sale.objects.filter(
                company=user.company
            )

            # ========================
            # FILTROS
            # ========================

            if branch_id:
                query = query.filter(branch_id=branch_id)

            if key:
                query = query.filter(
                    Q(reference__icontains=key) |
                    Q(name_sale__icontains=key)
                )

            if customer_id:
                query = query.filter(
                    customer_id=customer_id
                )

            if user_id:
                query = query.filter(
                    user_id=user_id
                )

            if date_start:
                date_start = Plus.convert_to_utc(
                    date_start,
                    user.timezone
                )

                query = query.filter(
                    creationDate__date__gte=date_start
                )

            if date_end:
                date_end = Plus.convert_to_utc(
                    date_end,
                    user.timezone
                )

                query = query.filter(
                    creationDate__date__lte=date_end
                )

            if status and status != 'all':
                query = query.filter(
                    status=status
                )

            # ========================
            # RESUMEN GLOBAL
            # ========================

            summary = {

                "total_sales":
                    query.count(),

                "accepted_sales":
                    query.filter(
                        status='accepted'
                    ).count(),

                "pending_sales":
                    query.filter(
                        status='pending'
                    ).count(),

                "paid_sales":
                    query.filter(
                        status='paid'
                    ).count(),

                "cancelled_sales":
                    query.filter(
                        status='cancelled'
                    ).count(),

                "total_amount":
                    query.aggregate(
                        total=Sum('total')
                    )['total'] or 0,

                "total_paid":
                    query.aggregate(
                        total=Sum('amount_paid')
                    )['total'] or 0,

                "total_balance":
                    query.aggregate(
                        total=Sum('balance')
                    )['total'] or 0,

                "accepted_amount":
                    query.filter(
                        status='accepted'
                    ).aggregate(
                        total=Sum('total')
                    )['total'] or 0,

                "pending_amount":
                    query.filter(
                        status='pending'
                    ).aggregate(
                        total=Sum('total')
                    )['total'] or 0,

                "paid_amount":
                    query.filter(
                        status='paid'
                    ).aggregate(
                        total=Sum('total')
                    )['total'] or 0,

                "cancelled_amount":
                    query.filter(
                        status='cancelled'
                    ).aggregate(
                        total=Sum('total')
                    )['total'] or 0,
            }

            # ========================
            # ORDEN
            # ========================

            query = query.order_by(
                '-creationDate',
                '-id'
            )

            # ========================
            # PAGINACIÓN
            # ========================

            paginator = Paginator(
                query,
                20
            )

            try:
                page_obj = paginator.page(page)

            except PageNotAnInteger:
                page_obj = paginator.page(1)

            except EmptyPage:
                page_obj = paginator.page(
                    paginator.num_pages
                )

            results = []

            for sale in page_obj:

                date = Plus.convert_from_utc(
                    sale.creationDate,
                    user.timezone
                )

                formatted_date = (
                    Plus.format_date_to_text(
                        date.isoformat(),
                        user.language,
                        1
                    )
                )

                user_name = (
                    sale.user.name
                    if sale.user
                    else 'Doc.'
                )

                photo = (
                    sale.user.avatar.url
                    if sale.user and sale.user.avatar
                    else '/static/img/employees-select.webp'
                )

                results.append({

                    "id": sale.id,

                    "reference": sale.reference,

                    "name_sale":
                        sale.name_sale
                        if sale.name_sale
                        else 'sales.navbar.new',

                    "customer":
                        sale.customer.name
                        if sale.customer
                        else 'sales.label.public',

                    "photo_user": photo,

                    "user": user_name,

                    "total": sale.total,

                    "amount_paid": sale.amount_paid,

                    "balance": sale.balance,

                    "currency": sale.currency,

                    "status": sale.status,

                    "creationDate": formatted_date,

                    "branch":
                        sale.branch.name_branch
                        if sale.branch
                        else None
                })

            return {

                "success": True,

                "message": "",

                "error": "",

                "answer": results,

                "summary": summary,

                "pagination": {
                    "page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_records": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }

        except Exception as e:

            return {

                "success": False,

                "message": "",

                "error": str(e),

                "answer": [],

                "summary": {},

                "pagination": {}
            }
