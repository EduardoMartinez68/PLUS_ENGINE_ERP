from core.plus.services import ServiceRegistry
from core.Plus import Plus
from decimal import Decimal
from core.plus.decorators import require_permission
from apps.payroll.models import PayrollPeriod, Payroll, EmployeeContract, EmployeeTablePayrollPeriod
from core.models import CustomUser, Company
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from apps.sales.models import SalePaymentMethod
from apps.sales.models import Sale

class PayrollPeriodService:
    @staticmethod
    @require_permission("view_payroll_period")
    @ServiceRegistry.register(
        "payroll.PayrollPeriodService.search_payroll_periods"
    )
    def search_payroll_periods(user, query, start_date, end_date, status, page):
        """
        Search payroll periods.

        Params:
            query: Search by Payroll.reference.
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            status: OPEN, CLOSED, PAID
            page: Page number.
            page_size: Records per page.
        """
        page_size = 10

        filters = Q(company=user.company)

        # Search by payroll reference
        if query:
            filters &= Q(payroll__reference__icontains=query)

        # Search by date range (period overlaps the selected range)
        if start_date and end_date:
            filters &= (
                Q(start_date__lte=end_date) &
                Q(end_date__gte=start_date)
            )
        elif start_date:
            filters &= Q(end_date__gte=start_date)
        elif end_date:
            filters &= Q(start_date__lte=end_date)

        # Status
        if status:
            filters &= Q(status=status)

        payroll_periods = (
            PayrollPeriod.objects
            .filter(filters)
            .annotate(
                employees_count=Count("employeetablepayrollperiod")
            )
            .distinct()
            .order_by("-start_date")
        )

        paginator = Paginator(payroll_periods, page_size)
        page_obj = paginator.get_page(page)

        periods_list = []

        for period in page_obj:
            periods_list.append({
                "id": period.id,
                "employees_count": period.employees_count,
                "start_date": period.start_date,
                "end_date": period.end_date,
                "payment_date": period.payment_date,
                "status": period.status,
                "pay_cash": period.pay_cash,
                "pay_card": period.pay_card,
                "pay_transfer": period.pay_transfer,
                "pay_paycheck": period.pay_terminal,
                "total": period.total,
            })

        return {
            "success": True,
            "answer": periods_list,
            "pagination": {
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_records": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "error": "The payroll periods were found successfully."
        }


    @staticmethod
    @require_permission("create_payroll_period")
    @ServiceRegistry.register(
        "payroll.PayrollPeriodService.create_payroll_period"
    )
    @transaction.atomic
    def create_payroll_period(user, data):
        """
        Create a payroll period and automatically add all active employee
        contracts to the period.
        """
        start_date = data["start_date"] or None
        end_date = data.get("end_date") or None

        if start_date and end_date and end_date < start_date:
            return {
                "success": False,
                "message": "End date cannot be before start date."
            }

        #now we will to conver this to UTC
        #only convert to utc if exist the date
        start_date = Plus.convert_from_utc(start_date, user.timezone)
        end_date = Plus.convert_from_utc(end_date, user.timezone)

        period = PayrollPeriod.objects.create(
            company=user.company,
            start_date=start_date,
            end_date=end_date,
            payment_date=timezone.now().date(),
            status="OPEN",
            pay_cash=0,
            pay_card=0,
            pay_transfer=0,
            pay_terminal=0,
            total=0,
        )

        # Obtain all active contracts for this company
        contracts = EmployeeContract.objects.filter(
            company=user.company,
            active=True
        )

        employees_period = [
            EmployeeTablePayrollPeriod(
                payrollPeriod=period,
                Employee=contract,
                status="OPEN"
            )
            for contract in contracts
        ]

        EmployeeTablePayrollPeriod.objects.bulk_create(employees_period)

        return {
            "success": True,
            "answer": {
                "id": period.id
            },
            "error": "The payroll period was created successfully."
        }

    #=============================================================#
    @staticmethod
    @require_permission("view_payroll_period")
    @ServiceRegistry.register(
        "payroll.PayrollPeriodService.search_employees_payroll_period"
    )
    def search_employees_payroll_period(user, query, payroll_period_id, page):
        """
        Search employees inside a payroll period.

        Params:
            payroll_period_id : int
            query             : username (optional)
            page              : int (default=1)

        Returns:
            List of employees belonging to the payroll period and, if it exists,
            the payroll assigned to each employee.
        """
        filters = Q(
            payrollPeriod_id=payroll_period_id,
            Employee__company=user.company
        )

        if query:
            filters &= Q(Employee__employee__username__icontains=query)

        employees = (
            EmployeeTablePayrollPeriod.objects
            .select_related(
                "Employee",
                "Employee__employee",
                "payrollPeriod"
            )
            .filter(filters)
            .order_by("Employee__employee__username")
        )

        paginator = Paginator(employees, 20)
        page_obj = paginator.get_page(page)

        employees_list = []

        with transaction.atomic():

            for item in page_obj:
                payroll, created = Payroll.objects.get_or_create(
                    employee_period=item, 
                    defaults={
                        "period": item.payrollPeriod,
                        "company": user.company,
                        "employee": item.Employee.employee,

                        "base_salary": item.Employee.salary,
                        "overtime": 0,
                        "commissions": 0,
                        "bonuses": 0,
                        "deductions": 0,
                        "total": item.Employee.salary,

                        "employee_signature_json": {},
                        "employee_signed_at": None,
                        "manager_signature_json": {},
                        "manager_signed_at": None,

                        "user_paid": None,
                    }
                )

                employees_list.append({
                    "id": payroll.id,
                    "employee_table_period_id": item.id,
                    "employee_contract_id": item.Employee.id,
                    "employee_id": item.Employee.employee.id,
                    "username": item.Employee.employee.username,
                    "salary": item.Employee.salary,
                    "salary_type": item.Employee.salary_type,
                    "status": item.status,

                    "payroll": {
                        "id": payroll.id,
                        "reference": payroll.reference,
                        "base_salary": payroll.base_salary,
                        "overtime": payroll.overtime,
                        "commissions": payroll.commissions,
                        "bonuses": payroll.bonuses,
                        "deductions": payroll.deductions,
                        "total": payroll.total,
                        "employee_signed": payroll.employee_signed_at is not None,
                        "manager_signed": payroll.manager_signed_at is not None,
                    }
                })

        return {
            "success": True,
            "answer": employees_list,
            "pagination": {
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_records": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "error": "The employees were found successfully."
        }

    @staticmethod
    @require_permission("view_payroll")
    @ServiceRegistry.register(
        "payroll.PayrollService.get_payroll"
    )
    def get_payroll(user, payroll_id):
        """
        Get payroll information.

        Params:
            payroll_id: int
        """
        try:
            payroll = (
                Payroll.objects
                .select_related(
                    "employee",
                    "period",
                    "user_paid"
                )
                .get(
                    id=payroll_id,
                    company=user.company
                )
            )

        except Payroll.DoesNotExist:
            return {
                "success": False,
                "answer": None,
                "error": "Payroll was not found."
            }

        return {
            "success": True,
            "answer": {
                "id": payroll.id,
                "reference": payroll.reference,

                "employee": {
                    "id": payroll.employee.id,
                    "username": payroll.employee.username,
                    "name": payroll.employee.name,
                },

                "status": payroll.employee_period.status,
                
                "period": {
                    "id": payroll.period.id,
                    "start_date": payroll.period.start_date,
                    "end_date": payroll.period.end_date,
                    "status": payroll.period.status,
                    "payment_date":Plus.format_date_to_text(Plus.convert_from_utc(payroll.payment_date, user.timezone), user.language) if  payroll.payment_date else '',
                },
                "commission_percentage": payroll.commission_percentage,
                "base_salary": payroll.base_salary,
                "overtime": payroll.overtime,
                "commissions": payroll.commissions,
                "bonuses": payroll.bonuses,
                "deductions": payroll.deductions,
                "total": payroll.total,

                "employee_signature_json": payroll.employee_signature_json,
                "employee_signed_at": payroll.employee_signed_at,

                "manager_signature_json": payroll.manager_signature_json,
                "manager_signed_at": payroll.manager_signed_at,

                "user_paid": (
                    None if payroll.user_paid is None else {
                        "id": payroll.user_paid.id,
                        "username": payroll.user_paid.username,
                    }
                ),
            },
            "error": "The payroll was obtained successfully."
        }

    @staticmethod
    @require_permission("pay_payroll")
    @ServiceRegistry.register(
        "payroll.PayrollService.buy_payroll"
    )
    def buy_payroll(user, payroll_id, data):
        """
        Pay an employee payroll.

        Params:
            payroll_id : int
            data : {
                base_salary,
                overtime,
                commissions,
                bonuses,
                deductions,
                total,
                method
            }
        """

        try:
            with transaction.atomic():
                #get the payroll with the ID 
                payroll = (
                    Payroll.objects
                    .select_related(
                        "period",
                        "employee_period"
                    )
                    .select_for_update()
                    .get(
                        id=payroll_id,
                        company=user.company
                    )
                )

                #here we will to see if can update the information of the table 
                #only can update the information of the table if the payroll is <open>
                status = payroll.employee_period.status
                if status == "PAID":
                    return {
                        "success": False,
                        "answer": None,
                        "error": "This payroll has already been paid."
                    }
                if status == "CLOSED":
                    return {
                        "success": False,
                        "answer": None,
                        "error": "This payroll period is closed."
                    }
                
                #now we see if the user inside the method of buy 
                method = data.get("method")
                if method not in ("cash", "card", "transfer", "terminal"):
                    return {
                        "success": False,
                        "answer": None,
                        "error": "Invalid payment method."
                    }

                #update all the information of the salary 
                payroll.base_salary = Decimal(data["base_salary"])
                payroll.overtime = Decimal(data["overtime"])
                payroll.bonuses = Decimal(data["bonuses"])
                payroll.deductions = Decimal(data["deductions"])
                payroll.total = Decimal(data["total"])
                payroll.user_paid = user
                payroll.payment_date=timezone.now()
                payroll.save()

                #update the status in <EmployeeTablePayrollPeriod> for know that this payroll was paid
                payroll.employee_period.status = "PAID"
                payroll.employee_period.save(update_fields=["status"])
                period = payroll.period

                # If all employees in this payroll period have been paid,
                # mark the payroll period as PAID.
                pending_payrolls = EmployeeTablePayrollPeriod.objects.filter(
                    payrollPeriod=period
                ).exclude(
                    status="PAID"
                ).exists()

                if not pending_payrolls:
                    period.status = "PAID"
                    
                if method == "cash":
                    period.pay_cash += payroll.total

                elif method == "card":
                    period.pay_card += payroll.total

                elif method == "transfer":
                    period.pay_transfer += payroll.total

                elif method == "terminal":
                    period.pay_terminal += payroll.total

                period.total = (
                    period.pay_cash
                    + period.pay_card
                    + period.pay_transfer
                    + period.pay_terminal
                )

                period.save(
                    update_fields=[
                        "status", 
                        "pay_cash",
                        "pay_card",
                        "pay_transfer",
                        "pay_terminal",
                        "total",
                    ]
                )

                #save this move of money in the records of the company
                SalePaymentMethod.objects.create(
                    company=user.company,
                    branch=user.branch,
                    user=user,

                    method=method,
                    amount=-payroll.total,

                    comment=f"Pago de Nomina ({payroll.reference})"
                )

                #update all the sales for know that this sales was mark as collected
                Sale.objects.filter(
                    company=user.company,
                    user=payroll.employee,
                    commission_made=False,
                    status__in=["accepted", "paid"],
                    startDate__date__gte=payroll.period.start_date,
                    startDate__date__lte=payroll.period.end_date,
                ).update(
                    commission_made=True
                )

                return {
                    "success": True,
                    "answer": {
                        "id": payroll.id
                    },
                    "error": "Payroll paid successfully."
                }

        except Exception as e:
            print(e)
            return {
                "success": False,
                "answer": None,
                "error": str(e)
            }



    @staticmethod
    @require_permission("change_payroll")
    @ServiceRegistry.register(
        "payroll.PayrollService.calculate_commission"
    )
    def calculate_commission(user, payroll_id, percentage):
        """
        Calculate the commission of a payroll.

        Params:
            payroll_id : int
            percentage : decimal (Example: 30 = 30%)
        """

        try:
            with transaction.atomic():

                payroll = (
                    Payroll.objects
                    .select_related(
                        "period",
                        "employee_period",
                        "employee",
                    )
                    .select_for_update()
                    .get(
                        id=payroll_id,
                        company=user.company
                    )
                )

                if payroll.employee_period.status != "OPEN":
                    return {
                        "success": False,
                        "answer": None,
                        "error": "The payroll can no longer be modified."
                    }

                percentage = Decimal(str(percentage))

                sales = Sale.objects.filter(
                    company=user.company,
                    user=payroll.employee,
                    commission_made=False,
                    status__in=["accepted", "paid"],
                    startDate__date__gte=payroll.period.start_date,
                    startDate__date__lte=payroll.period.end_date,
                )

                total_sales = (
                    sales.aggregate(
                        total=Sum("total")
                    )["total"]
                    or Decimal("0.00")
                )

                commissions = (
                    total_sales * percentage
                ) / Decimal("100")

                payroll.commission_percentage = percentage
                payroll.commissions = commissions

                payroll.total = (
                    payroll.base_salary
                    + payroll.overtime
                    + payroll.commissions
                    + payroll.bonuses
                    - payroll.deductions
                )

                payroll.save(
                    update_fields=[
                        "commission_percentage",
                        "commissions",
                        "total",
                    ]
                )

                return {
                    "success": True,
                    "answer": {
                        "percentage": percentage,
                        "total_sales": total_sales,
                        "commission": commissions,
                        "payroll_total": payroll.total,
                    },
                    "error": "Commission calculated successfully."
                }

        except Payroll.DoesNotExist:
            return {
                "success": False,
                "answer": None,
                "error": "Payroll was not found."
            }