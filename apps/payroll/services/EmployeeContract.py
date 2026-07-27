from core.plus.services import ServiceRegistry
from core.Plus import Plus
from decimal import Decimal
from core.plus.decorators import require_permission
from apps.payroll.models import EmployeeContract
from core.models import CustomUser, Company

class EmployeeContractService:

    @staticmethod
    @require_permission("create_employee_contract")
    @ServiceRegistry.register(
        "payroll.EmployeeContractService.create_employee_contract"
    )
    def create_employee_contract(cls, user, data):
        # ----------------------------
        # Required fields
        # ----------------------------
        required_fields = [
            "employee",
            "company",
            "salary",
            "salary_type",
            "start_date",
        ]

        #here we need see if exist all the information in the form 
        for field in required_fields:
            if not data.get(field):
                return {
                    "success": False,
                    "message": f"{field} is required."
                }

        # ----------------------------
        # Employee
        # ----------------------------
        try:
            employee = CustomUser.objects.get(
                id=data["employee"]
            )
        except CustomUser.DoesNotExist:
            return {
                "success": False,
                "message": "Employee not found."
            }

        # ----------------------------
        # Company
        # ----------------------------
        try:
            company = Company.objects.get(
                id=data["company"]
            )
        except Company.DoesNotExist:
            return {
                "success": False,
                "message": "Company not found."
            }

        # ----------------------------
        # Salary
        # ----------------------------
        if Decimal(data["salary"]) <= 0:
            return {
                "success": False,
                "message": "Salary must be greater than zero."
            }

        # ----------------------------
        # Dates
        # ----------------------------
        start_date = data["start_date"]
        end_date = data.get("end_date")

        if end_date and end_date < start_date:
            return {
                "success": False,
                "message": "End date cannot be before start date."
            }

        # ----------------------------
        # Existing active contract
        # ----------------------------
        active_contract = EmployeeContract.objects.filter(
            employee=employee,
            active=True
        ).exists()

        if active_contract:
            return {
                "success": False,
                "message": "Employee already has an active contract."
            }

        # ----------------------------
        # Create
        # ----------------------------
        contract = EmployeeContract.objects.create(
            employee=employee,
            company=company,
            salary=data["salary"],
            salary_type=data["salary_type"],
            start_date=start_date,
            end_date=end_date,
            active=data.get("active", True)
        )

        return {
            "success": True,
            "message": "Employee contract created successfully.",
            "data": {
                "id": contract.id
            }
        }

