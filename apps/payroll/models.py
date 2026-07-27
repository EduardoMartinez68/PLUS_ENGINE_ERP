from core.models import Company, Branch, CustomUser
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError

''''
1. first the user create a period of pay 
when the user create a period of pay when save all the employees in the table of pay

2. the user inside to the period of pay and can see all the employees in the system 
the user can select one a one to the employees and be show all his information of pay in a table 
the user can edit this table and when all is success the user create the pay of the payroll of the employee, 
the employee be move to payroll paid. This information no can be edit.
NOTE: when the user do a click in the employee the UI show all his sales (that is paid) and his appointment 

3. When all the employee was paid, the payrollperiod be check like paid the PayrollPeriod change his status to PAID. 
'''

class EmployeeContract(models.Model):
    TYPE_SALARY = (
        ("MONTHLY", "Monthly"),
        ("WEEKLY", "Weekly"),
        ("BIWEEKLY", "Biweekly"),
        ("DAILY", "Daily"),
        ("HOURLY", "Hourly"),
    )

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    #this is the information of the contract 
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    salary_type = models.CharField(
        max_length=20,
        choices=TYPE_SALARY
    )
    start_date = models.DateField() #when the employee start to work in the company 
    end_date = models.DateField(
        null=True,
        blank=True
    ) #when the employee finished of work in the company 

    active = models.BooleanField(default=True) #if the contract is activate for can paid 

class PayrollPeriod(models.Model):
    STATUS = (
        ("OPEN","Open"),
        ("CLOSED","Closed"),
        ("PAID","Paid"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )


    start_date = models.DateField()
    end_date = models.DateField()
    payment_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="OPEN"
    )

    #information total of pay 
    pay_cash=models.DecimalField(max_digits=12, decimal_places=2)
    pay_card=models.DecimalField(max_digits=12, decimal_places=2)
    pay_transfer=models.DecimalField(max_digits=12, decimal_places=2)
    pay_terminal=models.DecimalField(max_digits=12, decimal_places=2)
    total=models.DecimalField(max_digits=12, decimal_places=2)

class EmployeeTablePayrollPeriod(models.Model):
    #this table is for save the <employees> that the user would like do his payroll in a period 
    #it is a table for save the employees that is activate in this time
    payrollPeriod = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE
    )
    Employee = models.ForeignKey(
        EmployeeContract,
        on_delete=models.CASCADE
    )

    STATUS = (
        ("OPEN","Open"),
        ("CLOSED","Closed"),
        ("PAID","Paid"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="OPEN"
    )


class Payroll(models.Model):
    #this is for save the key of search 
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE
    )
    reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True
    )

    #this is for know the employee that get his payroll 
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    #information of pay of the employee
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    overtime = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    commissions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    #information of signature of the employee and the manager 
    employee_signature_json = models.JSONField()
    employee_signed_at = models.DateTimeField()

    manager_signature_json = models.JSONField()
    manager_signed_at = models.DateTimeField(null=True, blank=True) 

    #this is for save the user that create this payroll
    user_paid = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_paid'
    )


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'employee', 'reference'],
                name='unique_reference_per_company_user'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()

        if self.pk:
            # We obtain the version of the object that is already stored in the database
            original = PayrollPeriod.objects.get(pk=self.pk)

            # Block: ONLY if it ALREADY had a previous date AND they try to change it to a different one
            if original.manager_signed_at is not None and original.manager_signed_at != self.manager_signed_at:
                raise ValidationError("The signature date has already been recorded and cannot be changed.")

            if original.employee_signed_at is not None and original.employee_signed_at != self.employee_signed_at:
                raise ValidationError("The employee's signature date has already been recorded and cannot be changed.")

        super().save(*args, **kwargs)

    def _generate_reference(self):
        # Prefijo usando IDs o códigos (Ej: PAY-C1-B2-00001)
        prefix = f"PAY-C{self.company_id}-B{self.employee_id}-"
        
        # Bloqueamos los registros coincidentes para prevenir race conditions (concurrencia)
        with transaction.atomic():
            last_payroll = (
                Payroll.objects.select_for_update()
                .filter(company=self.company, employee=self.employee, reference__startswith=prefix)
                .order_by('-id')
                .first()
            )

            if last_payroll and last_payroll.reference:
                # Extraemos el número secuencial final
                try:
                    last_number = int(last_payroll.reference.split('-')[-1])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1

            return f"{prefix}{new_number:05d}"



class PayrollPayment(models.Model):
    #this table is for have a history of payment method  
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE
    )
    payment_date = models.DateField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    PAYMENT_METHODS = [
        ('cash', 'cash'),
        ('card', 'card'),
        ('transfer', 'transfer'),
        ('Paycheck', 'paycheck')
    ]
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)

class EmployeeCommission(models.Model):
    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    description = models.CharField(
        max_length=255
    )
    sale_id = models.IntegerField(
        null=True,
        blank=True
    )

    date = models.DateField()
    paid = models.BooleanField(default=False)

class EmployeeBonus(models.Model):
    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    description = models.CharField(
        max_length=255
    )
    date = models.DateField()
    paid = models.BooleanField(default=False)

class EmployeeDeduction(models.Model):

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    description = models.CharField(
        max_length=255
    )
    date = models.DateField()
    paid = models.BooleanField(default=False)

#================table sales check===========================
#here we will to check that the employee check his work entry
class WorkEntry(models.Model):
    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    date = models.DateField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(
        null=True,
        blank=True
    )
    worked_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

#===this is for save the justification when the employee not save his work entry==
class EmployeeLeave(models.Model):
    TYPE = (
        ("VACATION","Vacation"),
        ("SICK","Sick"),
        ("PERMISSION","Permission"),
        ("ABSENCE","Absence"),
        ("MATERNITY","Maternity"),
        ("PATERNITY","Paternity"),
        ("OTHER","Other"),
    )
    STATUS = (
        ("PENDING","Pending"),
        ("APPROVED","Approved"),
        ("REJECTED","Rejected"),
    )

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    leave_type = models.CharField(
        max_length=20,
        choices=TYPE
    )

    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="PENDING"
    )


class LeaveAttachment(models.Model):
    leave = models.ForeignKey(
        EmployeeLeave,
        on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to="leave_files/"
    )

#===================================================================================#
