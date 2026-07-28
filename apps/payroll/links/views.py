from django.shortcuts import render
import json
from django.shortcuts import render
from django.http import JsonResponse
from core.plus.services import ServiceRegistry
from core.plus.decorators import require_permission
from apps.payroll.services.EmployeeContract import EmployeeContractService

def payroll_home(request):
    return render(request, 'payroll/home.html')

def view_employees_contracts(request):
    return render(request, 'payroll/employees_contracts.html')


def view_search_employees_contracts(request):
    if request.method == "GET":
        allFilters = request.GET.get("allFilters", "")
        page = request.GET.get("page", 1)
        filters = allFilters.split(",")
        query = filters[0] if len(filters) > 0 and filters[0] else None

        #run the service
        return JsonResponse(ServiceRegistry.execute(
            "payroll.EmployeeContractService.search_employee_contracts", 
            request.user, 
            query,
            page
        ))



    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

def create_employee_contract(request):
    if request.method == "GET":
        return render(request, "payroll/employee_contract_form.html")
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "answer": "message.invalid-json",
                "error": "El cuerpo de la petición no es un JSON válido"
            }, status=400)

        #run the service
        return ServiceRegistry.execute(
            "payroll.EmployeeContractService.create_employee_contract", 
            request.user, 
            data
        )

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

def update_employee_contract(request, contract_id):
    if request.method == "GET":
        return render(request, "payroll/employee_contract_form.html")
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "answer": "message.invalid-json",
                "error": "El cuerpo de la petición no es un JSON válido"
            }, status=400)

        #run the service
        return ServiceRegistry.execute(
            "payroll.EmployeeContractService.update_employee_contract", 
            request.user, 
            data
        )

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

def get_employee_contract(request, contract_id):
    if request.method == "GET":
        return ServiceRegistry.execute(
            "payroll.EmployeeContractService.get_employee_contract_by_id", 
            request.user,
            contract_id
        )
    
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 