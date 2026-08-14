#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.payroll.services.Sales import SalesService
from apps.payroll.services.PayrollPeriod import PayrollPeriodService
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
            return JsonResponse(ServiceRegistry.execute(
                "payroll.EmployeeContractService.create_employee_contract", 
                request.user, 
                data
            ))
    
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
            return JsonResponse(ServiceRegistry.execute(
                "payroll.EmployeeContractService.update_employee_contract", 
                request.user, 
                contract_id,
                data
            ))
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def get_employee_contract(request, contract_id):
        if request.method == "GET":
            return JsonResponse(ServiceRegistry.execute(
                "payroll.EmployeeContractService.get_employee_contract_by_id", 
                request.user,
                contract_id
            ))
        
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def search_payrollperiod(request):
        if request.method == "GET":
            allFilters = request.GET.get("allFilters", "")
            page = request.GET.get("page", 1)
            filters = allFilters.split(",")
            query = filters[0] if len(filters) > 0 and filters[0] else None
            start_date = filters[1] if len(filters) > 1 and filters[1] else None
            end_date = filters[2] if len(filters) > 2 and filters[2] else None
            status = filters[3] if len(filters) > 3 and filters[3] else None
    
            #run the service
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollPeriodService.search_payroll_periods", 
                request.user, 
                query, 
                start_date, 
                end_date, 
                status, 
                page
            ))
    
    
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def create_payrollperiod(request):
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
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollPeriodService.create_payroll_period", 
                request.user, 
                data
            ))
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def view_payrollperiod(request, payrollperiod_id):
        context = {
            'payrollperiod_id': payrollperiod_id
        }
        return render(request, 'payroll/view_payrollperiod.html', context)

@login_required(login_url='login')
def search_payroll(request):
        if request.method == "GET":
            allFilters = request.GET.get("allFilters", "")
            page = request.GET.get("page", 1)
            filters = allFilters.split(",")
            query = filters[0] if len(filters) > 0 and filters[0] else None
            payroll_period_id = filters[1] if len(filters) > 1 and filters[1] else None
            
            #run the service
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollPeriodService.search_employees_payroll_period", 
                request.user, 
                query, 
                payroll_period_id,
                page
            ))
    
    
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def get_payroll_by_id(request, payroll_id):
        if request.method == "GET":
            #run the service
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollService.get_payroll", 
                request.user, 
                payroll_id
            ))
    
    
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def buy_payroll(request, payroll_id):
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
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollService.buy_payroll", 
                request.user, 
                payroll_id,
                data
            ))
    
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def create_payroll(request):
        return render(request, 'payroll/create_payroll.html') 

@login_required(login_url='login')
def search_sale(request, payroll_period_id):
        if request.method == "GET":
            allFilters = request.GET.get("allFilters", "")
            page = request.GET.get("page", 1)
            filters = allFilters.split(",")
            query = filters[0] if len(filters) > 0 and filters[0] else None
            employee_id = filters[1] if len(filters) > 1 and filters[1] else None
    
            #run the service
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollService.search_sales_for_commissions", 
                request.user, 
                payroll_period_id,
                employee_id,
                page,
            ))
    
    
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def get_total_sale(request, payroll_period_id):
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
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollService.calculate_sales_for_commissions", 
                request.user, 
                payroll_period_id,
                data.get('employee_id')
            ))
    
    
    
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 

@login_required(login_url='login')
def update_commissions(request, payroll_id):
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
            return JsonResponse(ServiceRegistry.execute(
                "payroll.PayrollService.calculate_commission", 
                request.user, 
                payroll_id,
                data.get("percentage", 0)
            ))

