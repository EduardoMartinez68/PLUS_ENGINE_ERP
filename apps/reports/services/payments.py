
from ..plus_wrapper import Plus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from apps.sales.models import Sale, SaleItem, Pack, SaleHistory, SalePaymentMethod
from django.db.models import Sum, Q
from decimal import Decimal

class ReportsPayments:
    @classmethod
    def search_move(cls, user, key=None, page=1,
                          branch_id=None, user_id=None,
                          date_start=None, date_end=None,
                          method=None):

        try:
            query = SalePaymentMethod.objects.filter(company=user.company, branch=user.branch)

            # 🔎 1. Búsqueda por comentario
            if key:
                query = query.filter(
                    Q(comment__icontains=key)
                )

            # 🏢 2. Filtro por sucursal
            if branch_id:
                query = query.filter(branch_id=branch_id)

            # 👤 3. Filtro por usuario
            if user_id:
                query = query.filter(user_id=user_id)

            # 💳 4. Filtro por método de pago
            if method:
                query = query.filter(method=method)

            # 📅 5. Filtro por fechas
            if date_start:
                date_start = Plus.convert_to_utc(date_start, user.timezone)
                query = query.filter(date__date__gte=date_start)

            if date_end:
                date_end = Plus.convert_to_utc(date_end, user.timezone)
                query = query.filter(date__date__lte=date_end)

            # 🔥 Orden
            query = query.order_by('-date', '-id')

            #now we will to calculate the totals of the moves
            totals = query.aggregate(
                total_income=Sum('amount', filter=Q(amount__gt=0)),
                total_expense=Sum('amount', filter=Q(amount__lt=0)),
                net_balance=Sum('amount')
            )

            total_income = totals['total_income'] or Decimal('0.00')
            total_expense = abs(totals['total_expense'] or Decimal('0.00'))
            net_balance = totals['net_balance'] or Decimal('0.00')
            movement_count = query.count()

            # 📄 Paginación
            paginator = Paginator(query, 20)

            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            results = []

            for item in page_obj:
                date = Plus.convert_from_utc(item.date, user.timezone) if item.date else None
                formatted_date = Plus.format_date_to_text(
                    date.isoformat(), user.language, 1
                ) if date else None

                amount=item.amount
                type_move='inside' if amount>=0 else 'outside'
                results.append({
                    "id": item.id,
                    "method": item.method,
                    "amount": str(amount),
                    "comment": item.comment if item.comment else '',
                    "date": formatted_date,
                    "type_move": type_move,

                    # Relaciones
                    "sale_id": item.sale.id if item.sale else None,
                    "payment_id": item.payment.id if item.payment else None,
                    "branch_name": item.branch.name_branch if item.branch else None,

                    # Usuario
                    "user": item.user.name if item.user else None,
                    "photo_user": item.user.avatar.url if item.user and item.user.avatar else '/static/img/employees-select.webp',
                })

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer": results,
                "pagination": {
                    "page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_records": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                },
                "summary": {
                    "total_income": str(total_income),   
                    "total_expense": str(total_expense),
                    "net_balance": str(net_balance),   
                    "movement_count": movement_count,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": str(e),
                "answer": [],
                "pagination": {}
            }