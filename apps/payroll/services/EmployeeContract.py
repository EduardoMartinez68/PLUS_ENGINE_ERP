from core.plus.services import ServiceRegistry
from core.Plus import Plus
from decimal import Decimal
from core.plus.decorators import require_permission
from apps.payroll.models import EmployeeContract
from core.models import CustomUser, Company
from django.core.paginator import Paginator
from django.db.models import Q


class EmployeeContractService:

    @staticmethod
    @require_permission("create_employee_contract")
    @ServiceRegistry.register(
        "payroll.EmployeeContractService.create_employee_contract"
    )
    def create_employee_contract(user, data):
        # ----------------------------
        # Required fields
        # ----------------------------
        required_fields = [
            "employee",
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
        company = employee.company

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
        end_date = data.get("end_date") or None

        if end_date and end_date < start_date:
            return {
                "success": False,
                "message": "End date cannot be before start date."
            }

        #now we will to conver this to UTC
        #only convert to utc if exist the date
        if start_date:
            start_date = Plus.convert_from_utc(start_date, user.timezone)
            
        if end_date:
            end_date = Plus.convert_from_utc(end_date, user.timezone)

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
        try:
            contract = EmployeeContract.objects.create(
                employee=employee,
                company=company,
                salary=data["salary"],
                salary_type=data["salary_type"],
                start_date=start_date,
                end_date=end_date,
                active=Plus.to_bool(data.get("active", True))
            )
        except Exception as e:
            return {
                "success": False,
                "message": "Failed to create employee contract.",
                "error": str(e)
            }


        return {
            "success": True,
            "message": "Employee contract created successfully.",
            "data": {
                "id": contract.id
            }
        }

    @staticmethod
    @require_permission("update_employee_contract")
    @ServiceRegistry.register(
        "payroll.EmployeeContractService.update_employee_contract"
    )
    def update_employee_contract(user, contract_id, data):
        # ----------------------------
        # Contract Existence
        # ----------------------------
        try:
            contract = EmployeeContract.objects.get(id=contract_id)
        except EmployeeContract.DoesNotExist:
            return {
                "success": False,
                "message": "Employee contract not found."
            }

        # ----------------------------
        # Employee (optional update)
        # ----------------------------
        if "employee" in data:
            try:
                employee = CustomUser.objects.get(id=data["employee"])
                contract.employee = employee
            except CustomUser.DoesNotExist:
                return {
                    "success": False,
                    "message": "Employee not found."
                }
        else:
            employee = contract.employee

        # ----------------------------
        # Salary Validation
        # ----------------------------
        if "salary" in data:
            if Decimal(data["salary"]) <= 0:
                return {
                    "success": False,
                    "message": "Salary must be greater than zero."
                }
            contract.salary = data["salary"]

        # ----------------------------
        # Dates Validation
        # ----------------------------
        # ----------------------------
        # Dates
        # ----------------------------
        start_date = data["start_date"]
        end_date = data.get("end_date") or None

        if end_date and end_date < start_date:
            return {
                "success": False,
                "message": "End date cannot be before start date."
            }

        #now we will to conver this to UTC
        #only convert to utc if exist the date
        if start_date:
            start_date = Plus.convert_from_utc(start_date, user.timezone)
            
        if end_date:
            end_date = Plus.convert_from_utc(end_date, user.timezone)

        contract.start_date = start_date
        contract.end_date = end_date

        # ----------------------------
        # Active status / Active Contract Conflict
        # ----------------------------
        new_active_status = Plus.to_bool(data.get("active", False))

        # Si el contrato pasa a estar activo (o sigue activo) y cambia de empleado o estado,
        # validamos que no exista OTRO contrato activo para el mismo empleado.
        if new_active_status:
            active_contract_exists = EmployeeContract.objects.filter(
                employee=employee,
                active=True
            ).exclude(id=contract.id).exists()

            if active_contract_exists:
                return {
                    "success": False,
                    "message": "Employee already has another active contract."
                }

        contract.active = new_active_status

        # ----------------------------
        # Other simple fields
        # ----------------------------
        if "salary_type" in data:
            contract.salary_type = data["salary_type"]

        # ----------------------------
        # Save changes
        # ----------------------------
        contract.save()

        return {
            "success": True,
            "message": "Employee contract updated successfully.",
            "data": {
                "id": contract.id
            }
        }


    @staticmethod
    @require_permission("view_employee_contract")
    @ServiceRegistry.register(
        "payroll.EmployeeContractService.get_employee_contract_by_id"
    )
    def get_employee_contract_by_id(user, contract_id):
        # ----------------------------
        # Contract Fetch
        # ----------------------------
        try:
            contract = EmployeeContract.objects.select_related(
                "employee", 
                "company"
            ).get(id=contract_id)
        except EmployeeContract.DoesNotExist:
            return {
                "success": False,
                "message": "Employee contract not found."
            }

        # ----------------------------
        # Response Formatting
        # ----------------------------
        return {
            "success": True,
            "message": "Employee contract retrieved successfully.",
            "answer": {
                "id": contract.id,
                "employee": {
                    "id": contract.employee.id,
                    "first_name": getattr(contract.employee, "first_name", None),
                    "last_name": getattr(contract.employee, "last_name", None),
                    "email": getattr(contract.employee, "email", None),
                },
                "company": {
                    "id": contract.company.id,
                    "name": getattr(contract.company, "name", None),
                },
                "salary": contract.salary,
                "salary_type": contract.salary_type,
                "start_date": contract.start_date.strftime("%Y-%m-%d") if contract.start_date else None,
                "end_date": contract.end_date.strftime("%Y-%m-%d") if contract.end_date else None,
                "active": contract.active,
                "created_at": contract.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(contract, "created_at") and contract.created_at else None,
            }
        }


    @staticmethod
    @require_permission("view_employee_contract")
    @ServiceRegistry.register(
        "payroll.EmployeeContractService.search_employee_contracts"
    )
    def search_employee_contracts(user, query, page_number):
        # ----------------------------
        # Parámetros de entrada
        # ----------------------------
        # data puede ser un dict enviado por la petición (ej: request.GET o JSON)
        per_page = 20

        # ----------------------------
        # Consulta Base con Optimización
        # ----------------------------
        queryset = EmployeeContract.objects.select_related(
            "employee", "company"
        ).order_by("-id")

        # ----------------------------
        # Filtro por username del empleado
        # ----------------------------
        if query:
            # icontains busca de manera insensible a mayúsculas/minúsculas
            queryset = queryset.filter(
                Q(employee__username__icontains=query) |
                Q(employee__name__icontains=query) |
                Q(employee__email__icontains=query)
            )

        # ----------------------------
        # Paginación (primeros 20 o por página)
        # ----------------------------
        paginator = Paginator(queryset, per_page)
        
        try:
            page_obj = paginator.page(page_number)
        except Exception:
            page_obj = paginator.page(1)

        # ----------------------------
        # Formateo de Resultados (List Stream)
        # ----------------------------
        contracts_list = []
        for contract in page_obj.object_list:
            contracts_list.append({
                "id": contract.id,
                "email": contract.employee.email,
                "avatar": contract.employee.avatar.url if contract.employee.avatar else '/static/img/profile-employees.webp',
                "username":contract.employee.username,
                "name":contract.employee.name,
                "branch_name":contract.employee.branch.name_branch,
                "salary": str(contract.salary),
                "salary_type": contract.salary_type,
                "start_date": contract.start_date.strftime("%Y-%m-%d") if contract.start_date else '---',
                "end_date": contract.end_date.strftime("%Y-%m-%d") if contract.end_date else '---',
                "active": contract.active,
            })

        # ----------------------------
        # Respuesta JSON estandarizada
        # ----------------------------
        return {
            "success": True,
            "answer": contracts_list,
            "pagination": {
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_records": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "error": "the search of the customer was success"
        }