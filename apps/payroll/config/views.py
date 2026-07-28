#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.payroll.services.EmployeeContract import EmployeeContractService
from core.plus.decorators import require_permission
from core.plus.services import ServiceRegistry
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.shortcuts import render
@login_required(login_url='login')
def payroll_home(request):
        return render(request, 'payroll/home.html')

@login_required(login_url='login')
def view_employees_contracts(request):
        return render(request, 'payroll/employees_contracts.html')

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def get_employee_contract(request, contract_id):
        if request.method == "GET":
            return ServiceRegistry.execute(
                "payroll.EmployeeContractService.get_employee_contract_by_id", 
                request.user,
                contract_id
            )
        
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

